---
sidebar_position: 2
---

# PTQ Principles and Step-by-Step Guide

### Introduction{#PTQ_introduction}

Model conversion refers to the process of converting an original floating-point model into a D-Robotics hybrid heterogeneous model. The original floating-point model (also referred to as a floating-point model in some places in this document) is a usable model you obtain by training with DL frameworks such as TensorFlow/PyTorch, with float32 computation precision. A hybrid heterogeneous model is a model format suitable for running on D-Robotics processors.
This chapter will repeatedly use these two model terms. To avoid ambiguity, please understand these concepts before reading further.

The complete model development process with the D-Robotics algorithm toolchain requires five important stages: **Floating-Point Model Preparation**, **Model Verification**, **Model Conversion**, **Performance Evaluation**, and **Accuracy Evaluation**, as shown below:

![model_conversion_flowchart](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/model_conversion_flowchart.png)


**Floating-Point Model Preparation** This stage ensures that the original floating-point model format is supported by the D-Robotics model conversion tool. The original floating-point model comes from a usable model you train with DL frameworks such as TensorFlow/PyTorch. For specific floating-point model requirements and recommendations, please read the [**Floating-Point Model Preparation**](#model_preparation) section.

**Model Verification** This stage verifies whether the original floating-point model meets the requirements of the D-Robotics algorithm toolchain. D-Robotics provides the ``hb_mapper checker`` tool to check floating-point models. For detailed usage, please read the [**Model Verification**](#model_check) section.

**Model Conversion** This stage completes the conversion from a floating-point model to a D-Robotics hybrid heterogeneous model. After this stage, you will obtain a model that can run on D-Robotics processors. D-Robotics provides the ``hb_mapper makertbin`` conversion tool to complete key steps such as model optimization, quantization, and compilation. For detailed usage, please read the [**Model Conversion**](#model_conversion) section.

**Performance Evaluation** This stage mainly evaluates the inference performance of D-Robotics hybrid heterogeneous models. D-Robotics provides model performance evaluation tools. You can use these tools to verify whether model performance meets application requirements. For detailed instructions, please read the [**Model Performance Analysis and Tuning**](#performance_evaluation) section.

**Accuracy Evaluation** This stage mainly evaluates the inference accuracy of D-Robotics hybrid heterogeneous models. D-Robotics provides model accuracy evaluation tools. For detailed instructions, please read the [**Model Accuracy Analysis and Tuning**](#accuracy_evaluation) section.



### Floating-Point Model Preparation{#model_preparation}


Floating-point models trained with public DL frameworks are the input to the D-Robotics model conversion tool. The DL frameworks currently supported by the conversion tool are as follows:


  | **Framework**         | Caffe | PyTorch | TensorFlow | MXNet | PaddlePaddle |
  |-------|------------|--------------|--------------|--------------|--------------|
  | **D-Robotics Toolchain** | Supported  |   Supported (convert to ONNX)|Supported (convert to ONNX)|Supported (convert to ONNX)|Supported (convert to ONNX)|


Among the frameworks above, caffemodel exported from the Caffe framework is directly supported. DL frameworks such as PyTorch, TensorFlow, and MXNet are indirectly supported by converting to ONNX format.

Standardized solutions are available for converting different frameworks to ONNX. Refer to the following:

-    Pytorch2Onnx: The PyTorch official API supports exporting models directly to ONNX. Reference link:
         https://pytorch.org/tutorials/advanced/super_resolution_with_onnxruntime.html

-    Tensorflow2Onnx: Convert using onnx/tensorflow-onnx from the ONNX community. Reference link:
         https://github.com/onnx/tensorflow-onnx

-    MXNet2Onnx: The MXNet official API supports exporting models directly to ONNX. Reference link:
         https://github.com/dotnet/machinelearning/blob/main/test/Microsoft.ML.Tests/OnnxConversionTest.cs

-    For ONNX conversion support for more frameworks, reference link:
         https://github.com/onnx/tutorials#converting-to-onnx-format


:::tip Tip

  For models from PyTorch, PaddlePaddle, and TensorFlow2 frameworks, we also provide tutorials on exporting ONNX and model visualization. Please refer to:

  - [**PyTorch ONNX Export and Model Visualization Tutorial**](https://developer.d-robotics.cc/forumDetail/146177165367615499) ;

  - [**PaddlePaddle ONNX Export and Model Visualization Tutorial**](https://developer.d-robotics.cc/forumDetail/146177165367615500) ;

  - [**TensorFlow2 ONNX Export and Model Visualization Tutorial**](https://developer.d-robotics.cc/forumDetail/146177165367615501) ;
:::

:::note Note

  - Operators used in the floating-point model must comply with the operator constraints of the D-Robotics algorithm toolchain. Please refer to the [**Model Operator Support List**](./supported_op_list) section for details.

  - Currently, the conversion tool only supports models with 32 or fewer outputs.
  
  - Supports quantizing Caffe floating-point models of ``caffe 1.0`` and ONNX floating-point models with ``ir_version≤7``, ``opset=10``, and ``opset=11`` into fixed-point models supported by D-Robotics. For the correspondence between ONNX model ir_version and ONNX version, please refer to the [**ONNX official documentation**](https://github.com/onnx/onnx/blob/main/docs/Versioning.md) ;

  - Model input dimensions only support ``fixed 4-dimensional`` NCHW or NHWC input (N dimension must be 1), for example: 1x3x224x224 or 1x224x224x3. Dynamic dimensions and non-4-dimensional inputs are not supported;

  - Do not include ``post-processing operators`` in the floating-point model, such as the NMS operator.

:::

### Model Verification{#model_check}


Before formal model conversion, please use the ``hb_mapper checker`` tool for model verification to ensure it meets the support constraints of D-Robotics processors.

:::tip Tip

  It is recommended to refer to the script methods for Caffe, ONNX, and other example models in the D-Robotics model conversion ``horizon_model_convert_sample`` sample package: ``01_check_X3.sh``.
:::
#### Using the ``hb_mapper checker`` Tool to Verify Models
```
The usage of the hb_mapper checker tool is as follows:
```
```
  hb_mapper checker --model-type ${model_type} \
                    --march ${march} \
                    --proto ${proto} \
                    --model ${caffe_model/onnx_model} \
                    --input-shape ${input_node} ${input_shape} \
                    --output ${output}
```

hb_mapper checker parameter descriptions:

--model-type<br/>
  Used to specify the type of model to check. Currently only ``caffe`` or ``onnx`` is supported.

--march
  Used to specify the D-Robotics processor type to adapt to. Valid values are ``bernoulli2`` and ``bayes``; set to ``bernoulli2`` for RDK X3 and ``bayes-e`` for RDK X5.

--proto<br/>
  This parameter is only valid when ``model-type`` is set to ``caffe``. The value is the prototxt file name of the Caffe model.

--model<br/>
  When ``model-type`` is set to ``caffe``, the value is the caffemodel file name of the Caffe model.
  When ``model-type`` is set to ``onnx``, the value is the ONNX model file name.

--input-shape<br/>
  Optional parameter to explicitly specify the input shape of the model.
  The value is ``{input_name} {NxHxWxC/NxCxHxW}``, with a space between ``input_name`` and shape.
  For example, if the model input name is ``data1`` and the input shape is ``[1,224,224,3]``,
  the configuration should be ``--input-shape data1 1x224x224x3``.
  If the shape configured here differs from the shape in the model, the configuration here takes precedence.
:::note Note
  Note that one ``--input-shape`` accepts only one name and shape combination. If your model has multiple input nodes,
  configure the ``--input-shape`` parameter multiple times in the command.
:::

:::note Note
  The ``--output`` parameter has been deprecated. Log information is stored in ``hb_mapper_checker.log`` by default.
:::



#### Handling Check Exceptions

If the model check step terminates abnormally or error messages appear, model verification has failed. Please check the error messages and modification suggestions in the terminal output or in the ``hb_mapper_checker.log`` log file generated in the current directory.

For example, the following configuration contains an unrecognized operator type ``Accuracy``:

```
  layer {
    name: "data"
    type: "Input"
    top: "data"
    input_param { shape: { dim: 1 dim: 3 dim: 224 dim: 224 } }
  }
  layer {
    name: "Convolution1"
    type: "Convolution"
    bottom: "data"
    top: "Convolution1"
    convolution_param {
      num_output: 128
      bias_term: false
      pad: 0
      kernel_size: 1
      group: 1
      stride: 1
      weight_filler {
        type: "msra"
      }
    }
  }
  layer {
    name: "accuracy"
    type: "Accuracy"
    bottom: "Convolution3"
    top: "accuracy"
    include {
      phase: TEST
    }
  }
```
When you use ``hb_mapper checker`` to check this model, you will get the following information in ``hb_mapper_checker.log``:

```bash
  ValueError: Not support layer name=accuracy type=Accuracy
```

:::note Note

  - If the model check step terminates abnormally or error messages appear, model verification has failed. Please check the error messages and modification suggestions in the terminal output or in the ``hb_mapper_checker.log`` log file generated in the current directory. You can look up solutions in the [**Model Quantization Errors and Solutions**](../../../08_FAQ/05_toolchain.md#model_convert_errors_and_solutions) section. If the issue persists, please contact the D-Robotics technical support team or post your question on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc/). We will provide support within 24 hours.
:::


#### Interpreting Check Results{#check_result}

If there are no ERROR messages, verification passes successfully. The ``hb_mapper checker`` tool will directly output the following information:

```
  ==============================================
  Node         ON   Subgraph  Type
  ----------
  conv1        BPU  id(0)     HzSQuantizedConv
  conv2_1/dw   BPU  id(0)     HzSQuantizedConv
  conv2_1/sep  BPU  id(0)     HzSQuantizedConv
  conv2_2/dw   BPU  id(0)     HzSQuantizedConv
  conv2_2/sep  BPU  id(0)     HzSQuantizedConv
  conv3_1/dw   BPU  id(0)     HzSQuantizedConv
  conv3_1/sep  BPU  id(0)     HzSQuantizedConv
  ...
```

Each line in the result represents the check status of a model node. Each line contains four columns: Node, ON, Subgraph, and Type, representing the node name, the hardware executing the node computation, the subgraph the node belongs to, and the D-Robotics operator name mapped to the node.
If CPU-computed operators appear in the model network structure, the hb_mapper checker tool will split the consecutive BPU-computed parts before and after such operators into two Subgraphs.

#### Tuning Guidance Based on Check Results

In the ideal case, all operators in the model network structure should run on the BPU, meaning there is only one subgraph. If CPU operators cause the model to be split into multiple subgraphs, the ``hb_mapper checker`` tool will provide the specific reason for the CPU operators. The following shows an example model verification case on RDK X3;

- The following Caffe model running on **RDK X3** contains a Reshape + Pow + Reshape structure. From the operator constraint list for **RDK X3**, we can see that the Reshape operator currently runs on the CPU, and the shape of Pow is non-4-dimensional, which does not meet the X3 BPU operator constraints.

![model_reshape](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/model_reshape.png)


Therefore, the final check result will also show segmentation, as follows:

```
  2022-05-25 15:16:14,667 INFO The converted model node information:
  ====================================================================================
  Node                                    ON   Subgraph  Type
  -------------
  conv68                                  BPU  id(0)     HzSQuantizedConv
  sigmoid16                               BPU  id(0)     HzLut
  axpy_prod16                             BPU  id(0)     HzSQuantizedMul
  UNIT_CONV_FOR_eltwise_layer16_add_1     BPU  id(0)     HzSQuantizedConv
  prelu49                                 BPU  id(0)     HzPRelu
  fc1                                     BPU  id(0)     HzSQuantizedConv
  fc1_reshape_0                           CPU  --        Reshape
  fc_output/square                        CPU  --        Pow
  fc_output/sum_pre_reshape               CPU  --        Reshape
  fc_output/sum                           BPU  id(1)     HzSQuantizedConv
  fc_output/sum_reshape_0                 CPU  --        Reshape
  fc_output/sqrt                          CPU  --        Pow
  fc_output/expand_pre_reshape            CPU  --        Reshape
  fc_output/expand                        BPU  id(2)     HzSQuantizedConv
  fc1_reshape_1                           CPU  --        Reshape
  fc_output/expand_reshape_0              CPU  --        Reshape
  fc_output/op                            CPU  --        Mul

```


Based on the hints from hb_mapper checker, operators running on the BPU generally deliver better performance. Here, CPU operators such as Pow and Reshape can be removed from the model, and their functionality can be moved to post-processing to reduce the number of subgraphs.

Of course, multiple subgraphs will not affect the overall conversion process, but they will significantly impact model performance. It is recommended to adjust model operators to run on the BPU as much as possible. You can refer to the BPU operator support list in the D-Robotics processor operator support list to replace operators with equivalent functionality, or move CPU operators in the model to pre-processing or post-processing for CPU computation.


### Model Conversion{#model_conversion}

The model conversion stage completes the conversion from a floating-point model to a D-Robotics hybrid heterogeneous model. After this stage, you will obtain a model that can run on D-Robotics processors.
Before conversion, please ensure that you have successfully passed the model verification process described above.

Model conversion is performed using the ``hb_mapper makertbin`` tool. During conversion, important processes such as model optimization and calibration quantization are completed. Calibration requires preparing calibration data according to model pre-processing requirements.
To help you fully understand model conversion, this section will introduce calibration data preparation, conversion tool usage, interpretation of the internal conversion process, interpretation of conversion results, and interpretation of conversion outputs in sequence.


#### Preparing Calibration Data

During model conversion, the calibration stage requires approximately **100** calibration sample inputs, with each sample being an independent data file.
To ensure the accuracy of the converted model, we recommend that these calibration samples come from the **training set or validation set** used to train your model. Do not use very rare outlier samples, such as **solid-color images or images containing no detection or classification targets**.

The ``preprocess_on`` parameter in the conversion configuration file corresponds to two different pre-processing sample requirements when enabled and disabled, respectively.
(For detailed parameter configuration, refer to the related descriptions in the calibration parameter group below.)
When ``preprocess_on`` is disabled, you need to apply the same pre-processing to samples taken from the training/validation set as before model inference,
so that the processed calibration samples have the same data type (``input_type_train``), size (``input_shape``), and
layout (``input_layout_train``) as the original model. For models with featuremap input, you can save data as float32 binary files using the ``numpy.tofile`` command,
and the toolchain will read them using the ``numpy.fromfile`` command during calibration.
For example, for an original floating-point model trained on ImageNet for classification with a single input node, the input information is as follows:

- Input type: ``BGR``
- Input layout: ``NCHW``
- Input size: ``1x3x224x224``

The data pre-processing when using the validation set for model inference is as follows:

1. Scale the image proportionally, with the short side scaled to 256.
2. Use the ``center_crop`` method to obtain a 224x224 image.
3. Subtract mean per channel.
4. Multiply data by the scale coefficient.

The sample processing code for the above example model is as follows:

To avoid lengthy code, implementations of various simple transformers are not included here. For specific usage, please refer to the [**Transformer Usage**](../../../08_FAQ/05_toolchain.md#transposetransformer) section.

:::tip Tip

  It is recommended to refer to the pre-processing step methods for Caffe, ONNX, and other example models in the D-Robotics model conversion ``horizon_model_convert_sample`` sample package: ``02_preprocess.sh`` and ``preprocess.py``.
:::
```
  # This example uses skimage; opencv would differ slightly
  # Note that subtract-mean and multiply-scale are not shown in transformers
  # mean and scale operations are fused into the model; see norm_type/mean_value/scale_value below
  def data_transformer():
    transformers = [
    # Proportional scale; short side scaled to 256
    ShortSideResizeTransformer(short_size=256),
    # CenterCrop to obtain 224x224 image
    CenterCropTransformer(crop_size=224),
    # skimage reads in NHWC layout; convert to NCHW required by the model
    HWC2CHWTransformer(),
    # skimage reads RGB channel order; convert to BGR required by the model
    RGB2BGRTransformer(),
    # skimage reads values in [0.0,1.0]; adjust to the value range required by the model
    ScaleTransformer(scale_value=255)
    ]

    return transformers

  # src_image original image from calibration set
  # dst_file file name to store final calibration sample data
  def convert_image(src_image, dst_file, transformers)：
    image = skimage.img_as_float(skimage.io.imread(src_file))
    for trans in transformers:
    image = trans(image)
    # input_type_train BGR numeric type specified by the model is UINT8
    image = image.astype(np.uint8)
    # Store calibration sample as binary to data file
    image.tofile(dst_file)

  if __name__ == '__main__':
    # Original calibration image collection; pseudocode
    src_images = ['ILSVRC2012_val_00000001.JPEG'，...]
    # Final calibration file names (extension not restricted); pseudocode
    # calibration_data_bgr_f32 is the cal_data_dir you specify in the config file
    dst_files = ['./calibration_data_bgr_f32/ILSVRC2012_val_00000001.bgr'，...]

    transformers = data_transformer()
    for src_image, dst_file in zip(src_images, dst_files):
    convert_image(src_image, dst_file, transformers)
```

:::note Note
  When ``preprocess_on`` is enabled, calibration samples can use image format files supported by skimage.
  After the conversion tool reads these images, it will resize them to the size required by the model input node and use the result as calibration input.
  This approach is simpler, but does not guarantee quantization accuracy. Therefore, we strongly recommend using ``preprocess_on`` in the disabled state.

:::note Note
  Note that the ``input_shape`` parameter in the yaml file specifies the input data size of the original floating-point model. For dynamic-input models, you can use this parameter to set the input size after conversion, and the calibration data shape must be consistent with ``input_shape``.
  
  For example: if the original floating-point model input node shape is ?x3x224x224 ("?" represents a placeholder, meaning the first dimension is dynamic input), and ``input_shape: 8x3x224x224`` is set in the conversion config file, then each calibration data sample prepared by the user must be 8x3x224x224.
  (Please note that for models whose input shape first dimension is not equal to 1, modifying model batch information via the ``input_batch`` parameter is not supported.)
:::


#### Using the hb_mapper makertbin Tool to Convert Models{#makertbin}

hb_mapper makertbin provides two modes: with ``fast-perf`` mode enabled and without ``fast-perf`` mode enabled.

When ``fast-perf`` mode is enabled, a bin model that can run at the highest performance on the board is generated during conversion. The tool mainly performs the following operations internally:

- Run BPU-executable operators on the BPU as much as possible (for ``RDK X5``, you can specify operators to run on the BPU via the ``node_info`` parameter in the yaml file; ``RDK X3`` uses automatic optimization and cannot specify operators via the yaml config file).

- Remove non-removable CPU operators at the beginning and end of the model, including: Quantize/Dequantize, Transpose, Cast, Reshape, etc.

- Compile the model with the highest-performance O3 optimization level.

:::tip Tip

  It is recommended to refer to the script methods for Caffe, ONNX, and other example models in the D-Robotics model conversion ``horizon_model_convert_sample`` sample package: ``03_build_X3.sh``.
:::

The usage of the hb_mapper makertbin command is as follows:

Without ``fast-perf`` mode:

```bash

  hb_mapper makertbin --config ${config_file}  \
                      --model-type  ${model_type}
```

With ``fast-perf`` mode:

```bash

  hb_mapper makertbin --fast-perf --model ${caffe_model/onnx_model} --model-type ${model_type} \
                      --proto ${caffe_proto} \
                      --march ${march}
```

hb_mapper makertbin parameter descriptions:

--help<br/>
  Display help information and exit.

-c, --config<br/>
  Model compilation configuration file in yaml format with a .yaml suffix. For a complete configuration file template, refer to the section below.

--model-type<br/>
  Used to specify the type of model to convert. Currently ``caffe`` or ``onnx`` is supported.

--fast-perf<br/>
  Enable fast-perf mode. When enabled, a bin model that can run at the highest performance on the board is generated during conversion for subsequent model performance evaluation.

  If you enable fast-perf mode, you also need the following configuration:

  --model<br/>
  Caffe or ONNX floating-point model file.

  --proto<br/>
  Used to specify the Caffe model prototxt file.

  --march<br/>
  BPU micro-architecture. Set to ``bernoulli2`` for ``RDK X3`` and ``bayes-e`` for ``RDK X5``.


:::note Note

  - For ``RDK X3 yaml configuration files``, you can directly use the [**RDK X3 Caffe Model Quantization yaml Template**](../../../08_FAQ/05_toolchain.md#rdk_x3_caffe_yaml_template) and [**RDK X3 ONNX Model Quantization yaml Template**](../../../08_FAQ/05_toolchain.md#rdk_x3_onnx_yaml_template) template files for filling in.


  - For ``RDK X5 yaml configuration files``, you can directly use the [**RDK X5 Caffe Model Quantization yaml Template**](../../../08_FAQ/05_toolchain.md#rdk_x5_caffe_yaml_template) and [**RDK X5 ONNX Model Quantization yaml Template**](../../../08_FAQ/05_toolchain.md#rdk_x5_onnx_yaml_template) template files for filling in.

  - If the hb_mapper makertbin step terminates abnormally or error messages appear, model conversion has failed. Please check the error messages and modification suggestions in the terminal output or in the ``hb_mapper_makertbin.log`` log file generated in the current directory. You can look up solutions in the [**Model Quantization Errors and Solutions**](../../../08_FAQ/05_toolchain.md#model_convert_errors_and_solutions) section. If the issue persists, please contact the D-Robotics technical support team or post your question on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc/). We will provide support within 24 hours.
:::

#### Model Conversion yaml Configuration Parameters{#yaml_config}

:::note Note
  Either a Caffe model or an ONNX model. That is, choose one of ``caffe_model`` + ``prototxt`` or ``onnx_model``.
  In other words, either a Caffe model or an ONNX model.
:::
```
  # Model parameter group
  model_parameters:
    # Original Caffe floating-point model description file
    prototxt: '***.prototxt'

    # Original Caffe floating-point model data file
    caffe_model: '****.caffemodel'

    # Original ONNX floating-point model file
    onnx_model: '****.onnx'

    # Target processor architecture for conversion; keep default. D-Robotics RDK X3 uses bernoulli2 architecture, RDK X5 uses bayes-e architecture. march: 'bayes-e'
    march: 'bernoulli2'

    # Name prefix for the model file output for on-board execution after model conversion
    output_model_file_prefix: 'mobilenetv1'

    # Directory for model conversion output results
    working_dir: './model_output_dir'

    # Whether the converted hybrid heterogeneous model retains intermediate results of each output layer; keep default
    layer_out_dump: False

    # Specify model output nodes
    output_nodes: {OP_name}

    # Batch delete nodes of a certain type
    remove_node_type: Dequantize

    # Delete nodes with specified names
    remove_node_name: {OP_name}

  # Input information parameter group
  input_parameters:
    # Input node name of the original floating-point model
    input_name: "data"

    # Input data format of the original floating-point model (count/order consistent with input_name)
    input_type_train: 'bgr'

    # Input data layout of the original floating-point model (count/order consistent with input_name)
    input_layout_train: 'NCHW'

    # Input data size of the original floating-point model
    input_shape: '1x3x224x224'

    # batch_size fed to the network during actual execution; default is 1
    input_batch: 1

    # Input data pre-processing method added to the model
    norm_type: 'data_mean_and_scale'

    # Mean subtracted from images in the pre-processing method; if channel means, values must be separated by spaces
    mean_value: '103.94 116.78 123.68'

    # Image scale factor in the pre-processing method; if per-channel scale, values must be separated by spaces
    scale_value: '0.017'

    # Input data format the converted hybrid heterogeneous model needs to adapt to (count/order consistent with input_name)
    input_type_rt: 'yuv444'

    # Special format of input data
    input_space_and_range: 'regular'

    # Input data layout the converted hybrid heterogeneous model needs to adapt to (count/order consistent with input_name); if input_type_rt is nv12, this parameter does not need to be configured
    input_layout_rt: 'NHWC'

  # Calibration parameter group
  calibration_parameters:
    # Directory storing calibration samples used for model calibration
    cal_data_dir: './calibration_data'

    # Data storage type of calibration data binary files.
    cal_data_type: 'float32'

    # Enable automatic processing of image calibration samples (skimage read; resize to input node size)
    #preprocess_on: False  
    
    # Calibration algorithm type; default calibration algorithm is preferred
    calibration_type: 'default'

    # Parameters for max calibration method
    # max_percentile: 1.0

    # Force specified OP to run on CPU; generally not needed; can be enabled during accuracy tuning to try accuracy optimization
    #run_on_cpu:  {OP_name}

    # Force specified OP to run on BPU; generally not needed; can be enabled during performance tuning to try performance optimization
    # run_on_bpu:  {OP_name}

    # Specify whether to calibrate per channel
    #per_channel: False

    # Specify output node data precision
    #optimization: set_model_output_int8

  # Compiler parameter group
  compiler_parameters:
    # Compilation strategy selection
    compile_mode: 'latency'

    # Whether to enable compilation debug information; keep default False
    debug: False

    # Number of model execution cores
    core_num: 1

    # Model compilation optimization level; keep default O3
    optimize_level: 'O3'

    # Specify input data source for input named data
    #input_source: {"data": "pyramid"}

    # Specify maximum continuous execution time per function call of the model
    #max_time_per_fc: 1000

    # Specify number of processes when compiling the model
    #jobs: 8
	
  # This parameter group does not need configuration; only enable when using custom CPU operators
  #custom_op: 
    # Custom op calibration method; register method is recommended
    #custom_op_method: register

    # Custom OP implementation file; multiple files can be separated by ";"; can be generated from template; see custom OP documentation
    #op_register_files: sample_custom.py

    # Directory containing custom OP implementation files; use relative path
    #custom_op_dir: ./custom_op
```

The configuration file mainly contains the model parameter group, input information parameter group, calibration parameter group, and compiler parameter group.
In your configuration file, all four parameter groups must be present. Specific parameters are optional or required; optional parameters may be omitted.

The setting format for specific parameters is: ``param_name:  'param_value'`` ;
When a parameter has multiple values, separate each value with ``';'``: ``param_name:  'param_value1; param_value2; param_value3'`` ; for example: ``run_on_cpu: 'conv_0; conv_1; conv12'`` .

:::tip Tip
  
  - For multi-input models, it is recommended to explicitly specify optional parameters (``input_name``, ``input_shape``, etc.) to avoid errors in parameter order correspondence.


  - When configuring march as bayes-e, i.e., during RDK X5 model conversion, if you set optimize_level to O3, hb_mapper makertbin provides caching by default. That is, the first time you use hb_mapper makertbin to compile a model, a cache file is created automatically. On subsequent repeated compilations with the same working_dir, this file is called automatically to reduce compilation time.
:::

:::note Note

  - Note that if ``input_type_rt`` is set to ``nv12`` or ``yuv444``, odd numbers must not appear in the model input dimensions.
  - Note that RDK X3 currently does not support the combination of ``input_type_rt`` as ``yuv444`` and ``input_layout_rt`` as ``NCHW``.
  - After successful model conversion, if an OP that meets D-Robotics BPU operator constraints still runs on the CPU, the main reason is that the OP is a passively quantized OP. For passive quantization, please read the [**Active and Passive Quantization Logic in the Algorithm Toolchain**](https://developer.d-robotics.cc/forumDetail/118364000835765793) section.
:::

The following lists specific parameter information. There are many parameters; we introduce them in the order of the parameter groups above.


- ###### Model Parameter Group

| Parameter Name | Parameter Description | Value Range | Optional/Required |
|------------|----------|----------|--------|
|``prototxt``| **Purpose**: Specify the prototxt file name of the Caffe floating-point model.<br/>**Description**: Must be configured when ``hb_mapper makertbin`` ``model-type`` is ``caffe``.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``caffe_model``| **Purpose**: Specify the caffemodel file name of the Caffe floating-point model.<br/>**Description**: Must be configured when ``hb_mapper makertbin`` ``model-type`` is ``caffe``.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``onnx_model``| **Purpose**: Specify the onnx file name of the ONNX floating-point model.<br/>**Description**: Must be configured when ``hb_mapper makertbin`` ``model-type`` is ``onnx``.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``march``| **Purpose**: Specify the platform architecture the output hybrid heterogeneous model needs to support.<br/>**Description**: The two optional values correspond to the BPU micro-architectures of RDK X3 and RDK Ultra, respectively. Select according to your platform.| **Value Range**: ``bernoulli2`` or ``bayes``.<br/> **Default**: None.|Required |
|``output_model_file_prefix``| **Purpose**: Specify the name prefix of the output hybrid heterogeneous model after conversion.<br/>**Description**: Name prefix of the output fixed-point model file.| **Value Range**: None.<br/> **Default**: None.|Required |
|``working_dir``| **Purpose**: Specify the directory for model conversion output results.<br/>**Description**: If the directory does not exist, the tool creates it automatically.| **Value Range**: None.<br/> **Default**: ``model_output``.|Optional |
|``layer_out_dump``| **Purpose**: Specify whether the hybrid heterogeneous model retains intermediate layer output values.<br/>**Description**: Outputting intermediate layer values is a debugging technique; do not enable it under normal circumstances.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |
|``output_nodes``| **Purpose**: Specify model output nodes.<br/>**Description**: In general, the conversion tool automatically identifies model output nodes. This parameter supports specifying intermediate layers as outputs. Set the value to specific node names in the model. For multiple values, refer to the ``param_value`` configuration description above. Note that once this parameter is set, the tool no longer automatically identifies output nodes; the nodes you specify via this parameter are all outputs.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``remove_node_type``| **Purpose**: Set the type of nodes to delete.<br/>**Description**: This is a hidden parameter; not setting it or setting it empty does not affect model conversion. This parameter supports setting the type information of nodes to delete. Deleted nodes must be at the beginning or end of the model, connected to model input or output. Note: Nodes to delete are deleted sequentially in order, dynamically updating the model structure; before deletion, it is also checked whether the node is at model input/output. Therefore, node deletion order matters.| **Value Range**: "Quantize", "Transpose", "Dequantize", "Cast", "Reshape". Separate different types with ";".<br/> **Default**: None.|Optional |
|``remove_node_name``| **Purpose**: Set the name of nodes to delete.<br/>**Description**: This is a hidden parameter; not setting it or setting it empty does not affect model conversion. This parameter supports setting the names of nodes to delete. Deleted nodes must be at the beginning or end of the model, connected to model input or output. Note: Nodes to delete are deleted sequentially in order, dynamically updating the model structure; before deletion, it is also checked whether the node is at model input/output. Therefore, node deletion order matters.| **Value Range**: None. Separate different types with ";".<br/> **Default**: None.|Optional |
|``set_node_data_type``| **Purpose**: Configure the output data type of specified ops as int16. This parameter **only supports RDK Ultra and RDK X5 configuration!** <br/> **Description**: During model conversion, the default input/output data type of most ops is int8. This parameter can specify the output data type of specific ops as int16 (under certain constraints). For int16 details, see the [**int16 Configuration Description**](#int16_config) section. <br/> **Note:** The functionality of this parameter has been merged into the ``node_info`` parameter and is planned to be deprecated in future versions. | **Value Range**: For operators supporting int16 configuration, refer to the RDK Ultra and RDK X5 operator constraint lists in the [**Model Operator Support List**](./supported_op_list).<br/> **Default**: None.|Optional |
|``debug_mode``| **Purpose**: Save calibration data for accuracy debug analysis.<br/>**Description**: Saves calibration data for accuracy debug analysis in .npy format. This data can be loaded with np.load() and fed directly into the model for inference. If this parameter is not set, you can also save data yourself and use accuracy debug tools for analysis. | **Value Range**: ``"dump_calibration_data"``<br/> **Default**: None.|Optional |
|``node_info``| **Purpose**: Supports configuring specified OP input/output data types as int16 and forcing specified operators to run on CPU or BPU. This parameter **only supports RDK Ultra and RDK X5 configuration!** <br/>**Description**: Based on the principle of reducing parameters in yaml, we merged the capabilities of ``set_node_data_type``, ``run_on_cpu``, and ``run_on_bpu`` into this parameter, and extended support for configuring specified op input data types as int16.<br/> ``node_info`` parameter usage:  <br/>- Specify OP to run on BPU/CPU only (BPU example below; CPU method is the same):<br/> node_info:<br/> `{ "node_name" { 'ON': 'BPU',} }` <br/> - Specify OP to run on BPU and configure OP input/output data types:<br/> node_info:<br/> `{ "node_name": { 'ON': 'BPU', 'InputType': 'int16', 'OutputType': 'int16'}} ` <br/> - Specify multiple operators:<br/> node_info:<br/>`{"/model.0/conv/Conv": {"ON": "BPU","InputType": "int16","OutputType": "int16"},`<br/>`"/model.0/act/Mul": {"ON": "BPU","InputType": "int16","OutputType": "int16"},`<br/>`"/model.2/Concat": {"ON": "BPU","InputType": "int16","OutputType": "int16"}}`
'InputType': 'int16' means all input data types of the specified operator are int16. <br/>To specify InputType for a specific input of an operator, configure a number after InputType. For example:<br/>'InputType0': 'int16' means the first input data type of the specified operator is int16,<br/>'InputType1': 'int16' means the second input data type of the specified operator is int16, and so on.<br/>**Note:** 'OutputType' does not support specifying OutputType for specific outputs of an operator. Once configured, it applies to all outputs of the operator. 'OutputType0', 'OutputType1', etc. are not supported. | **Value Range**: For operators supporting int16 configuration, refer to the RDK Ultra and RDK X5 operator constraint lists in the [Model Operator Support List](./supported_op_list). Operators that can be specified to run on CPU or BPU must be operators contained in the model.<br/> **Default**: None.|Optional |

- ###### Input Information Parameter Group

| Parameter Name | Parameter Description | Value Range | Optional/Required |
|------------|----------|----------|--------|
|``input_name``| **Purpose**: Specify input node names of the original floating-point model.<br/>**Description**: Not required when the floating-point model has a single input node. Required when there are multiple input nodes to ensure correct order of subsequent types and calibration data input. For multiple values, refer to the param_value configuration description above.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``input_type_train``| **Purpose**: Specify input data types of the original floating-point model.<br/>**Description**: Each input node requires a definite input data type. When multiple input nodes exist, the order must strictly match that in ``input_name``. For multiple values, refer to the ``param_value`` configuration description above. For data type selection, refer to the Model Conversion Internal Process Interpretation section.| **Value Range**: ``rgb``, ``bgr``, ``yuv444``, ``gray``, ``featuremap``.<br/> **Default**: None.|Required |
|``input_layout_train``| **Purpose**: Specify input data layout of the original floating-point model.<br/>**Description**: Each input node requires a definite input data layout that must match the layout used by the original floating-point model. When multiple input nodes exist, the order must strictly match that in ``input_name``. For multiple values, refer to the ``param_value`` configuration description above. For data layout, refer to the Model Conversion Internal Process Interpretation section.| **Value Range**: NHWC, NCHW.<br/> **Default**: None.|Required |
|``input_type_rt``| **Purpose**: Input data format the converted hybrid heterogeneous model needs to adapt to.<br/>**Description**: This specifies the data format you need to use; it does not need to match the original model data format, but note that data fed to the model on the platform uses this format. Each input node requires a definite input data type. When multiple input nodes exist, the order must strictly match that in ``input_name``. For multiple values, refer to the ``param_value`` configuration description above. For data type selection, refer to the Model Conversion Internal Process Interpretation section.| **Value Range**: ``rgb``, ``bgr``, ``yuv444``, ``nv12``, ``gray``, ``featuremap``.<br/> **Default**: None.|Required |
|``input_layout_rt``| **Purpose**: Input data layout the converted hybrid heterogeneous model needs to adapt to.<br/>**Description**: Each input node requires a definite input data layout that you want to assign to the hybrid heterogeneous model. Inappropriate input data layout settings will affect performance; on X3 platform, NHWC format input is recommended. If input_type_rt is nv12, this parameter does not need to be configured. When multiple input nodes exist, the order must strictly match that in ``input_name``. For multiple values, refer to the ``param_value`` configuration description above. For data layout, refer to the Model Conversion Internal Process Interpretation section.| **Value Range**: ``NCHW``, ``NHWC``.<br/> **Default**: None.|Optional |
|``input_space_and_range``| **Purpose**: Specify special format of input data.<br/>**Description**: This parameter adapts to yuv420 formats output by different ISPs and is only effective when the corresponding input_type_rt is nv12. regular is the common yuv420 format with value range [0,255]; bt601_video is another video yuv420 format with value range [16,235]. More information about bt601 can be found online. Do not configure this parameter unless explicitly required.| **Value Range**: ``regular``, ``bt601_video``.<br/> **Default**: ``regular``.|Optional |
|``input_shape``| **Purpose**: Specify input data size of the original floating-point model.<br/>**Description**: Shape dimensions are connected with x, for example 1x3x224x224. When the original floating-point model has a single input node, this may be omitted and the tool reads size from the model file automatically. When configuring multiple input nodes, the order must strictly match that in ``input_name``. For multiple values, refer to the ``param_value`` configuration description above.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``input_batch``| **Purpose**: Specify input batch count the converted hybrid heterogeneous model needs to adapt to.<br/>**Description**: input_batch here is the input batch count of the converted hybrid heterogeneous bin model, but does not affect the input batch count of the converted onnx model. Default is 1 when not configured. This parameter only applies to single-input models, and the first dimension of ``input_shape`` must be 1.| **Value Range**: ``1-128``.<br/> **Default**: ``1``.|Optional |
|``norm_type``| **Purpose**: Input data pre-processing method added to the model.<br/>**Description**: ``no_preprocess`` means no data pre-processing is added; ``data_mean`` provides subtract-mean pre-processing; ``data_scale`` provides multiply-scale pre-processing; ``data_mean_and_scale`` provides subtract-mean then multiply-scale pre-processing. When there are multiple input nodes, the order must strictly match that in ``input_name``. For multiple values, refer to the ``param_value`` configuration description above. For the impact of this parameter, refer to the Model Conversion Internal Process Interpretation section.|**Value Range**: ``data_mean_and_scale``, ``data_mean``, ``data_scale``, ``no_preprocess``.<br/> **Default**: None.|Required |
|``mean_value``| **Purpose**: Specify mean subtracted from images in the pre-processing method.<br/>**Description**: Required when ``norm_type`` includes ``data_mean_and_scale`` or data_mean. For each input node, there are two configuration methods. The first is a single value meaning all channels subtract this mean; the second provides values equal to the number of channels (separated by spaces), meaning each channel subtracts a different mean. The number of configured input nodes must match the number of nodes in norm_type. If a node does not need mean processing, configure ``'None'`` for that node. For multiple values, refer to the ``param_value`` configuration description above.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``scale_value``| **Purpose**: Specify scale coefficient in the pre-processing method.<br/>**Description**: Required when ``norm_type`` includes ``data_mean_and_scale`` or ``data_scale``. For each input node, there are two configuration methods. The first is a single value meaning all channels multiply by this coefficient; the second provides values equal to the number of channels (separated by spaces), meaning each channel multiplies by a different coefficient. The number of configured input nodes must match the number of nodes in ``norm_type``. If a node does not need ``scale`` processing, configure ``'None'`` for that node. For multiple values, refer to the ``param_value`` configuration description above.| **Value Range**: None.<br/> **Default**: None.|Optional |

**input_type_rt/input_type_train Supplementary Description**

The RDK X5 compute platform architecture makes two assumptions for performance:

1. Assume input data is int8 quantized data.

2. Data captured by the camera is nv12.

Therefore, if you use rgb(NCHW) input format during model training but want this model to efficiently process nv12 data, configure as follows during model conversion:

```bash
  input_parameters:
      input_type_rt: 'nv12'
      input_type_train: 'rgb'
      input_layout_train: 'NCHW'
```

**Tip:**
- If you use gray format during model training but nv12 format in actual use, you can configure both ``input_type_rt`` and ``input_type_train`` as ``gray`` during model conversion, and use only the y channel address of nv12 as input in embedded application development.

- ###### Calibration Parameter Group

| Parameter Name | Parameter Description | Value Range | Optional/Required |
|------------|----------|----------|--------|
|``cal_data_dir``| **Purpose**: Specify the directory storing calibration samples used for model calibration.<br/>**Description**: Calibration data in the directory must meet input configuration requirements. Refer to the Preparing Calibration Data section. When configuring multiple input nodes, the order must strictly match that in ``input_name``. For multiple values, refer to the ``param_value`` configuration description above. When calibration_type is ``load`` or ``skip``, cal_data_dir is not required. Note: For convenience, if cal_data_type is not configured, we infer data type from folder suffix. If the folder suffix ends with ``_f32``, data type is float32; otherwise uint8. We strongly recommend constraining data type via the cal_data_type parameter.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``cal_data_type``| **Purpose**: Specify data storage type of calibration data binary files.<br/>**Description**: Specifies data storage type of binary files used during model calibration. If not specified, folder name suffix is used for inference.| **Value Range**: ``float32``, ``uint8``.<br/> **Default**: None.|Optional |
|``preprocess_on``| **Purpose**: Enable automatic processing of image calibration samples.<br/>**Description**: This option only applies to models with 4-dimensional image input; do not enable for non-4-dimensional models. When enabled, cal_data_dir contains jpg/bmp/png and other image data; the tool reads images with skimage and resizes to the size required by input nodes. To ensure calibration quality, keep this parameter disabled. For impact, refer to the Preparing Calibration Data section.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |
|``calibration_type``| **Purpose**: Calibration algorithm type.<br/>**Description**: Both ``kl`` and ``max`` are public calibration quantization algorithms; their basic principles can be found online. When using ``load`` calibration, the QAT model must be exported via plugin. ``mix`` is a search strategy integrating multiple calibration methods that automatically identifies quantization-sensitive nodes and selects the best method at node granularity from different calibration methods, ultimately building a combined calibration approach that fuses advantages of multiple methods. ``default`` is an automatic search strategy that tries to obtain a relatively good combination from a series of calibration quantization parameters. Try ``default`` first; if final accuracy does not meet expectations, configure different calibration parameters according to the Accuracy Tuning section. If you only want to verify model performance without accuracy requirements, try "skip" calibration, which uses random numbers and does not require calibration data, suitable for initial model structure validation. Note: With skip, because random numbers are used for calibration, the resulting model cannot be used for accuracy verification.| **Value Range**: ``default``, ``mix``, ``kl``, ``max``, ``load``, and ``skip``.<br/> **Default**: ``default``.|Required |
|``max_percentile``| **Purpose**: Parameter for the ``max`` calibration method to adjust the truncation point of ``max`` calibration.<br/>**Description**: Only effective when ``calibration_type`` is ``max``. Common options: 0.99999/0.99995/0.99990/0.99950/0.99900. Try ``calibration_type`` ``default`` first; if final accuracy does not meet expectations, adjust this parameter according to the Accuracy Tuning section.| **Value Range**: ``0.0``~``1.0``.<br/> **Default**: ``1.0``.|Optional |
|``per_channel``| **Purpose**: Control whether to calibrate per channel of featuremap.<br/>**Description**: Effective when ``calibration_type`` is not default. Try ``default`` first; if final accuracy does not meet expectations, adjust this parameter according to the Accuracy Tuning section.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |
|``run_on_cpu``| **Purpose**: Force specified operators to run on CPU.<br/>**Description**: Although CPU performance is inferior to BPU, it provides float-precision computation. If you determine certain operators must run on CPU, specify them via this parameter. Set the value to specific node names in the model. For multiple values, refer to the ``param_value`` configuration description above.<br/> **Note:** In **RDK Ultra and RDK X5**, functionality of this parameter has been merged into ``node_info`` and is planned to be deprecated in future versions. **RDK X3** continues to use it. | **Value Range**: None.<br/> **Default**: None.|Optional |
|``run_on_bpu``| **Purpose**: Force specified OP to run on BPU.<br/>**Description**: To ensure accuracy of the final quantized model, in some cases the conversion tool places operators that meet BPU computation conditions on CPU. If you have high performance requirements and accept more quantization loss, specify operators to run on BPU via this parameter. Set the value to specific node names in the model. For multiple values, refer to the ``param_value`` configuration description above.<br/> **Note:** In **RDK Ultra and RDK X5**, functionality of this parameter has been merged into ``node_info`` and is planned to be deprecated in future versions. **RDK X3** continues to use it.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``optimization``| **Purpose**: Make the model output in int8/int16 format.<br/>**Description**: When set to set_model_output_int8, sets the model to int8 low-precision output; when set to set_model_output_int16, sets the model to int16 low-precision output.<br/> **Note:** **RDK X3** only supports set_model_output_int8.<br/>**RDK Ultra and RDK X5** can set set_model_output_int8 or set_model_output_int16.|**Value Range**: ``set_model_output_int8`` or ``set_model_output_int16``.<br/> **Default**: None.|Optional |


- ###### Compiler Parameter Group

| Parameter Name | Parameter Description | Value Range | Optional/Required |
|------------|----------|----------|--------|
|``compile_mode``| **Purpose**: Compilation strategy selection.<br/>**Description**: ``latency`` optimizes for inference time; bandwidth optimizes for DDR access bandwidth. If the model does not significantly exceed expected bandwidth usage, use the ``latency`` strategy.| **Value Range**: ``latency``, ``bandwidth``.<br/> **Default**: ``latency``.|Required |
|``debug``| **Purpose**: Whether to enable compilation debug information.<br/>**Description**: When enabled, static analysis performance results of the model are saved in the model. After successful conversion, you can view per-layer BPU operator performance information (including computation amount, computation time, and data transfer time) in the Layer Details tab of the static performance evaluation HTML page and the HTML page generated by hb_perf. By default, keep this parameter disabled.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |
|``core_num``| **Purpose**: Number of model execution cores.<br/>**Description**: The D-Robotics platform supports using multiple AI accelerator cores simultaneously for one inference task. Multi-core is suitable for larger input sizes; ideally dual-core speed can reach about 1.5x single-core. If your model input size is large and you have extreme speed requirements, configure ``core_num=2``.<br/> **Note:** **RDK Ultra and RDK X5** do not support this option yet; default is 1, do not configure! | **Value Range**: ``1``, ``2``.<br/> **Default**: ``1``.|Optional |
|``optimize_level``| **Purpose**: Model compilation optimization level selection.<br/>**Description**: Optimization levels range from ``O0`` to ``O3``. ``O0`` applies no optimization, fastest compilation, lowest optimization. ``O1``-``O3`` increase optimization level; compiled model execution speed is expected to improve, but compilation time increases. Models for performance generation and verification must use ``O3`` to ensure optimal performance. For process verification or accuracy debugging, lower optimization levels can speed up the process.| **Value Range**: ``O0``, ``O1``, ``O2``, ``O3``.<br/> **Default**: None.|Required |
|``input_source``| **Purpose**: Set input data source for on-board bin model.<br/>**Description**: This parameter adapts to engineering environments; configure after completing all model verification. ``ddr`` means data comes from memory; ``pyramid`` and ``resizer`` mean data comes from fixed hardware on the processor. Note: if set to resizer, model h*w must be less than 18432. For adapting ``pyramid`` and ``resizer`` data sources in engineering environments, this parameter is configured specially; for example, if model input name is data and data source is memory (ddr), configure ``{"data": "ddr"}``.| **Value Range**: ``ddr``, ``pyramid``, ``resizer``<br/> **Default**: None; automatically selected from options based on input_type_rt by default.|Optional |
|``max_time_per_fc``| **Purpose**: Specify maximum continuous execution time per function-call of the model (unit: us).<br/>**Description**: When the compiled data-instruction model performs inference on the BPU, it appears as one or more function-call (BPU execution granularity) invocations. Value 0 means no limit. This parameter limits maximum execution time per function-call; the model can only be preempted when a single function-call completes. See Model Priority Control section for details. - This parameter is only for model preemption; ignore if preemption is not needed.<br/> - Model preemption is only supported on the development board, not on the PC simulator.| **Value Range**: ``0 or 1000-4294967295``.<br/> **Default**: ``0``.|Optional |
|``jobs``| **Purpose**: Set number of processes when compiling bin model.<br/>**Description**: Sets number of processes when compiling bin model; can improve compilation speed to some extent.| **Value Range**: Within maximum cores supported by the machine.<br/> **Default**: None.|Optional |


- ###### Custom Operator Parameter Group

| Parameter Name | Parameter Description | Value Range | Optional/Required |
|------------|----------|----------|--------|
|``custom_op_method``| **Purpose**: Custom operator strategy selection.<br/>**Description**: Currently only register strategy is supported.| **Value Range**: ``register``.<br/> **Default**: None.|Optional |
|``op_register_files``| **Purpose**: Python implementation file names of custom operators.<br/>**Description**: Multiple files can be separated by ``;``| **Value Range**: None.<br/> **Default**: None.|Optional |
|``custom_op_dir``| **Purpose**: Path storing Python implementation files of custom operators.<br/>**Description**: Use relative path when setting path.| **Value Range**: None.<br/> **Default**: None.|Optional |


##### RDK Ultra and RDK X5 int16 Configuration Description{#int16_config}
  
During model conversion, most operators in the model are quantized to int8 for computation. By configuring the ``node_info`` parameter,
you can specify input/output data types of certain ops as int16 (for supported operator range, refer to RDK Ultra and RDK X5 operator support lists in the [**Model Operator Support List**](./supported_op_list) section.
The basic principle is as follows:

After you configure an op's input/output data types as int16, model conversion internally automatically updates and checks int16 configuration of op input/output context.
For example, when configuring op_1 input/output as int16, it potentially specifies that op_1's upstream/downstream ops must support int16 computation.
For unsupported scenarios, the model conversion tool prints a log indicating the int16 configuration combination is temporarily unsupported and falls back to int8 computation.

##### Pre-processing HzPreprocess Operator Description{#pre_process}
The pre-processing HzPreprocess operator is a pre-processing operator node inserted after the model input node, generated by the D-Robotics model conversion tool during model conversion according to the yaml configuration file, used to normalize model input data. This section mainly describes the relationship between ``norm_type``, ``mean_value``, ``scale_value`` parameters and generation of the model pre-processing HzPreprocess operator node.

**norm_type Parameter Description**

- Purpose: Input data pre-processing method added to the model.

- Value range and description:

  - ``no_preprocess`` means no data pre-processing is added.
  - ``data_mean`` provides subtract-mean pre-processing.
  - ``data_scale`` provides multiply-scale pre-processing.
  - ``data_mean_and_scale`` provides subtract-mean then multiply-scale pre-processing.

:::note Note
  When there is more than one input node, the order must strictly match that in ``input_name``.
:::
