---
sidebar_position: 2
---

# Principles and Steps of PTQ

### Introduction {#PTQ_introduction}

Model conversion refers to the process of converting the original floating-point model to the Heterogeneous Line model. The original floating-point model (also referred to as the floating-point model in some places in this article) refers to the model you trained using DL frameworks such as TensorFlow/PyTorch, with a computational precision of float32. The Heterogeneous Line model is a model format that is suitable for running on the Heterogeneous Line processor.
This chapter will repeatedly use these two model terms. To avoid misunderstandings, please understand this concept before reading further.

The complete development process of the model with the Heterogeneous Line algorithm toolchain requires five important stages: **Floating-point Model Preparation**, **Model Verification**, **Model Conversion**, **Performance Evaluation**, and **Accuracy Evaluation**, as shown in the following diagram:

![model_conversion_flowchart](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/model_conversion_flowchart.png)


**Floating-point Model Preparation** This stage is used to ensure that the format of the original floating-point model is supported by the Heterogeneous Line model conversion tool. The original floating-point model is obtained from the available model trained by DL frameworks such as TensorFlow/PyTorch. For specific floating-point model requirements and recommendations, please refer to the [**Floating-point Model Preparation**](#model_preparation) section.

**Model Verification** This stage is used to verify whether the original floating-point model meets the requirements of the Heterogeneous Line algorithm toolchain. Heterogeneous Line provides the `hb_mapper checker` tool for checking floating-point models. For specific usage, please refer to the [**Model Verification**](#model_check) section.

**Model Conversion** This stage is used to perform the conversion from the floating-point model to the Heterogeneous Line heterogeneous model. After this stage, you will obtain a model that can run on the Heterogeneous Line processor. Heterogeneous Line provides the `hb_mapper makertbin` conversion tool to complete key steps such as model optimization, quantization, and compilation. For specific usage, please refer to the [**Model Conversion**](#model_conversion) section.

**Performance Evaluation** This stage is mainly used to evaluate the inference performance of the Heterogeneous Line heterogeneous model. Heterogeneous Line provides tools for model performance evaluation, which you can use to verify whether the model performance meets the application requirements. For specific usage instructions, please refer to the [**Model Performance Analysis and Tuning**](#performance_evaluation) section.

**Accuracy Evaluation** This stage is mainly used to evaluate the inference accuracy of the Heterogeneous Line heterogeneous model. Heterogeneous Line provides tools for model accuracy evaluation. For specific usage instructions, please refer to the [**Model Accuracy Analysis and Tuning**](#accuracy_evaluation) section.



### Model Preparation {#model_preparation}


The floating-point model obtained from publicly available DL frameworks is the input for the Heterogeneous Line model conversion tool. Currently, the conversion tool supports the following DL frameworks:


  | **Framework**   | Caffe | PyTorch | TensorFlow | MXNet | PaddlePaddle |
  |-------|------------|--------------|--------------|--------------|--------------|
  | **Heterogeneous Line Toolchain** | Supported  |   Supported (via ONNX conversion)|Supported (via ONNX conversion)|Supported (via ONNX conversion)|Supported (via ONNX conversion)|


Among these frameworks, the caffemodel exported by the Caffe framework is directly supported. PyTorch, TensorFlow, MXNet, and other DL frameworks are indirectly supported through conversion to the ONNX format.

For the conversion from different frameworks to ONNX, there are currently corresponding standard solutions, as follows:

-    Pytorch2Onnx: PyTorch official API supports exporting models directly as ONNX models. Refer to the link:
         https://pytorch.org/tutorials/advanced/super_resolution_with_onnxruntime.html

-    Tensorflow2Onnx: Conversion based on the onnx/tensorflow-onnx in the ONNX community. Refer to the link:
         https://github.com/onnx/tensorflow-onnx

-    MXNet2Onnx: MXNet official API supports exporting models directly as ONNX models. Refer to the link:https://github.com/dotnet/machinelearning/blob/main/test/Microsoft.ML.Tests/OnnxConversionTest.cs

-    More ONNX conversion support for other frameworks, please refer to the link: https://github.com/onnx/tutorials#converting-to-onnx-format

:::tip Tips

  We also provide tutorials on how to export ONNX and visualize models for Pytorch, PaddlePaddle, and TensorFlow2 frameworks. Please refer to:

  - [**Pytorch Export ONNX and Model Visualization Tutorial**](https://developer.d-robotics.cc/forumDetail/146177165367615499);

  - [**PaddlePaddle Export ONNX and Model Visualization Tutorial**](https://developer.d-robotics.cc/forumDetail/146177165367615500);

  - [**TensorFlow2 Export ONNX and Model Visualization Tutorial**](https://developer.d-robotics.cc/forumDetail/146177165367615501);
:::

:::caution Caution

  - Operators used in floating-point models need to comply with the operator constraint conditions of the D-Robotics algorithm toolchain. Please refer to the [**Supported Operator List**](./supported_op_list) section for details.

  - Currently, the conversion tool only supports the conversion of models with output count less than or equal to 32.

  - Supports quantization of ``caffe 1.0`` version floating-point models and ``ir_version ≤ 7``, ``opset=10``, ``opset=11`` versions of ONNX floating-point models into fixed-point models supported by Horizon. For the mapping between the IR version of the ONNX model and the ONNX version, please refer to the [**ONNX official documentation**](https://github.com/onnx/onnx/blob/main/docs/Versioning.md).

  - Model input dimensions only support ``fixed 4 dimensions`` input NCHW or NHWC (N dimension can only be 1), for example: 1x3x224x224 or 1x224x224x3. Dynamic dimensions and non-4D inputs are not supported.

  - Do not include ``post-processing operators`` in floating-point models, such as NMS operators.
:::

### Model Validation {#model_check}

Before formally converting the model, please use the ``hb_mapper checker`` tool to validate the model and ensure that it complies with the constraints supported by the D-Robotics processor.

:::tip Tips

  It is recommended to refer to the script methods ``01_check_X3.sh`` or ``01_check_Ultra.sh`` in the model conversion ``horizon_model_convert_sample`` example package of D-Robotics for examples of caffe, onnx, and other models.
:::

#### Validate the model using the ``hb_mapper checker`` tool
```
The usage of the hb_mapper checker tool is as follows:
```
```
  hb_mapper checker --model-type $`{`model_type`}` \
                    --march $`{`march`}` \
                    --proto $`{`proto`}` \
                    --model $`{`caffe_model/onnx_model`}` \
                    --input-shape $`{`input_node`}` $`{`input_shape`}` \
                    --output $`{`output`}`
```


hb_mapper checker parameters explanation:

--model-type<br/>
  Specifies the model type of the input for checking, currently only supports setting ``caffe`` or ``onnx``.

--march
  Specifies the D-Robotics processor type to be adapted, can be set to ``bernoulli2`` or ``bayes``; set to ``bernoulli2`` for RDK X3 and ``bayes`` for RDK Ultra.

--proto<br/>
  This parameter is only useful when ``model-type`` is set to ``caffe``, and its value is the prototxt file name of the Caffe model.

--model<br/>
  When ``model-type`` is specified as ``caffe``, its value is the caffemodel file name of the Caffe model.
  When ``model-type`` is specified as ``onnx``, its value is the name of the ONNX model file.

--input-shape<br/>
  Optional parameter, explicitly specifies the input shape of the model.
  Its value is ```{`input_name`}` `{`NxHxWxC/NxCxHxW`}```, with a space between ``input_name`` and the shape.
  For example, if the model input is named ``data1`` and the input shape is ``[1,224,224,3]``,
  then the configuration should be ``--input-shape data1 1x224x224x3``.
  If the configured shape here is inconsistent with the shape information inside the model, the shape configured here takes precedence.
:::info Remark
  Note that ``--input-shape`` only accepts one name-shape combination. If your model has multiple input nodes,
  you can configure the ``--input-shape`` parameter multiple times in the command.
:::

:::caution
  The -\-output parameter has been deprecated. The log information is stored in ``hb_mapper_checker.log`` by default.
:::



#### Handling Exceptions in Checking

If the model checking step terminates abnormally or error messages are displayed, it means that the model verification fails. Please refer to the error information printed on the terminal or the ``hb_mapper_checker.log`` log file generated in the current path for error information and modification suggestions.

For example: The following configuration contains an unrecognized operator type ``Accuracy``:

```
  layer `{`
    name: "data"
    type: "Input"
    top: "data"
    input_param `{` shape: `{` dim: 1 dim: 3 dim: 224 dim: 224 `}` `}`
  `}`
  layer `{`
    name: "Convolution1"
    type: "Convolution"
    bottom: "data"
    top: "Convolution1"
    convolution_param `{`
      num_output: 128
      bias_term: false
      pad: 0
      kernel_size: 1
      group: 1
      stride: 1
      weight_filler `{`
        type: "msra"
      `}`
    `}`
  `}`
  layer `{`
    name: "accuracy"
    type: "Accuracy"
    bottom: "Convolution3"
    top: "accuracy"
    include `{`
      phase: TEST
    `}`
  `}`
```
After using ``hb_mapper checker`` to check this model, you will get the following information in the ``hb_mapper_checker.log``:

```bash
  ValueError: Not support layer name=accuracy type=Accuracy
```

:::caution Note

  - If the model check step is terminated abnormally or there is an error message, it means that the model verification fails. Please confirm the error message and modification suggestions according to the terminal print or the generated ``hb_mapper_checker.log`` log file in the current path. You can find the solution to the error in the [Model Quantization Errors and Solutions](../../../08_FAQ/05_toolchain.md#model-quantization-errors-and-solutions-model_convert_errors_and_solutions) section. If the above steps still cannot resolve the problem, please contact the D-Robotics technical support team or submit your question in the [D-Robotics Official Developer Community](https://developer.d-robotics.cc/). We will provide support within 24 hours.
:::


#### Interpretation of the check results{#check_result}

If there is no ERROR, then the check is successful. The ``hb_mapper checker`` tool will directly output the following information:

```
  ==============================================
  Node         ON   Subgraph  Type
  ----------
  conv1        BPU  id(0)     HzSQuantizedConv
  conv2_1/dw   BPU  id(0)     HzSQuantizedConv
  conv2_1/sep  BPU  id(0)     HzSQuantizedConv
  conv2_2/dw   BPU  id(0)     HzSQuantizedConv
  conv2_2/sep  BPU  id(0)     HzSQuantizedConvconv3_1/dw BPU id(0) HzSQuantizedConv
conv3_1/sep BPU id(0) HzSQuantizedConv
...
```

The result of each line represents the checking status of a model node, with four columns: Node, ON, Subgraph, and Type. They represent the node name, the hardware on which the node is executed, the subgraph to which the node belongs, and the D-Robotics operator name to which the node is mapped. If the model contains CPU operators in the network structure, the hb_mapper checker tool will split the part before and after the CPU operator into two subgraphs.

#### Optimization Guide for Checking Results

Ideally, all operators in the model's network structure should run on the BPU, which means there is only one subgraph. If there are CPU operators causing multiple subgraphs to be split, the "hb_mapper checker" tool will provide the specific reasons for the appearance of the CPU operators. Below are examples of model verification on RDK X3 and RDK Ultra.

- The Caffe model running on "RDK X3" has a structure of Reshape + Pow + Reshape. According to the operator constraint list on "RDK X3", we can see that the Reshape operator is currently running on the CPU, and the shape of Pow is also non-4D, which does not meet the constraints of the X3 BPU operator.

![model_reshape](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/model_reshape.png)

Therefore, the final checking result of the model will also show segmentation, as follows:


```
2022-05-25 15:16:14,667 INFO The converted model node information:
====================================================================================
Node                                  ON   Subgraph  Type
-------------
conv68                                BPU  id(0)     HzSQuantizedConv
sigmoid16                             BPU  id(0)     HzLut
axpy_prod16                           BPU  id(0)     HzSQuantizedMul
UNIT_CONV_FOR_eltwise_layer16_add_1   BPU  id(0)     HzSQuantizedConv
prelu49                               BPU  id(0)     HzPRelu
fc1                                   BPU  id(0)     HzSQuantizedConv
fc1_reshape_0                         CPU  --        Reshape
fc_output/square                      CPU  --        Pow
fc_output/sum_pre_reshape             CPU  --        Reshape
fc_output/sum                         BPU  id(1)     HzSQuantizedConv
fc_output/sum_reshape_0               CPU  --        Reshape
fc_output/sqrt                        CPU  --        Pow
fc_output/expand_pre_reshape          CPU  --        Reshape
fc_output/expand                      BPU  id(2)     HzSQuantizedConv
fc1_reshape_1                         CPU  --        Reshape
fc_output/expand_reshape_0            CPU  --        Reshape
fc_output/op                          CPU  --        Mul

```

According to the prompts from the hb_mapper checker, generally, operators running on the BPU achieve better performance. Here, CPU operators such as pow and reshape can be removed from the model, and their functionality can be moved to post-processing for computation, thereby reducing the number of subgraphs.

Of course, having multiple subgraphs does not affect the overall conversion process, but it significantly impacts model performance. It is recommended to adjust model operators to run on the BPU whenever possible. Refer to the BPU operator support list in the D-Robotics Processor Operator Support List for functionally equivalent operator replacements or move CPU operators in the model to pre-processing or post-processing stages for CPU computation.

### Model Conversion {#model_conversion}

The model conversion phase completes the transformation from a floating-point model to a D-Robotics hybrid heterogeneous model. After this phase, you will obtain a model that can run on a D-Robotics processor. Before proceeding with the conversion, ensure that the previous model verification process has been successfully completed.

Model conversion is performed using the ``hb_mapper makertbin`` tool. During conversion, important processes such as model optimization and calibration quantization are completed. Calibration requires preparing calibration data according to the model’s preprocessing requirements. To help you fully understand model conversion, this section will cover calibration data preparation, tool usage, interpretation of the internal conversion process, interpretation of conversion results, and interpretation of conversion outputs.

#### Preparing Calibration Data

During model conversion, the calibration phase requires approximately **100 calibration samples**, each sample being an independent data file. To ensure the accuracy of the converted model, these calibration samples should come from the **training set or validation set** used for model training. Avoid using rare abnormal samples, such as **solid-color images, images without any detection or classification targets, etc.**

The ``preprocess_on`` parameter in the conversion configuration file corresponds to two different preprocessing sample requirements depending on whether it is enabled or disabled. (Refer to the calibration parameter group section for detailed parameter configuration.)

When ``preprocess_on`` is disabled, you need to apply the same preprocessing to samples from the training/validation set as you would before model inference. The processed calibration samples will have the same data type (``input_type_train``), dimensions (``input_shape``), and layout (``input_layout_train``) as the original model. For feature map inputs, you can save the data as a float32 binary file using the ``numpy.tofile`` command. The toolchain will read the data during calibration using the ``numpy.fromfile`` command.

For example, an original floating-point classification model trained on ImageNet with a single input node has the following input description:

- Input type: ``BGR``
- Input layout: ``NCHW``
- Input dimensions: ``1x3x224x224``

The data preprocessing steps during inference using the validation set are as follows:

1. Scale the image proportionally, resizing the shorter side to 256.
2. Use the ``center_crop`` method to obtain a 224x224 image.
3. Subtract the mean per channel.
4. Multiply the data by the scale coefficient.

Example code for processing samples for the above model is as follows:

To avoid lengthy code, various simple transformer implementations are not shown. For usage, refer to the [**transformer usage guide**](../../../08_FAQ/05_toolchain.md#transposetransformer) section.

:::tip Tip

  It is recommended to refer to the preprocessing steps in the D-Robotics model conversion ``horizon_model_convert_sample`` example package for Caffe, ONNX, etc.: ``02_preprocess.sh`` and ``preprocess.py``.
:::
```
  # This example uses skimage; results may differ with OpenCV.
  # Note that transformers do not include mean subtraction or scale multiplication.
  # Mean and scale operations have been integrated into the model. Refer to the norm_type/mean_value/scale_value configuration below.
  def data_transformer():
    transformers = [
    # Scale proportionally, resizing the shorter side to 256
    ShortSideResizeTransformer(short_size=256),
    # Obtain 224x224 image using CenterCrop
    CenterCropTransformer(crop_size=224),
    # skimage reads in NHWC layout; convert to NCHW as required by the model
    HWC2CHWTransformer(),
    # skimage reads in RGB channel order; convert to BGR as required by the model
    RGB2BGRTransformer(),
    # skimage reads values in [0.0,1.0]; adjust to the range required by the model
    ScaleTransformer(scale_value=255)
    ]

    return transformers

  # src_image: Original image from the calibration set
  # dst_file: Name of the file storing the final calibration sample data
  def convert_image(src_image, dst_file, transformers)：
    image = skimage.img_as_float(skimage.io.imread(src_file))
    for trans in transformers:
    image = trans(image)
    # The input_type_train BGR value type specified by the model is UINT8
    image = image.astype(np.uint8)
    # Store the calibration sample as binary data in the data file
    image.tofile(dst_file)

  if __name__ == '__main__':
    # Here represents the original set of calibration images (pseudocode)
    src_images = ['ILSVRC2012_val_00000001.JPEG'，...]
    # Here represents the final calibration file names (no restriction on suffixes; pseudocode)
    # calibration_data_bgr_f32 is the cal_data_dir specified in your configuration file
    dst_files = ['./calibration_data_bgr_f32/ILSVRC2012_val_00000001.bgr'，...]

    transformers = data_transformer()
    for src_image, dst_file in zip(src_images, dst_files):
    convert_image(src_image, dst_file, transformers)
```

:::info
  When ``preprocess_on`` is enabled, calibration samples can be image files in formats supported by skimage. The conversion tool reads these images and resizes them to the dimensions required by the model’s input node, using the result as input for calibration. While this simplifies the process, it does not guarantee quantization accuracy. Therefore, we strongly recommend disabling ``preprocess_on``.

:::caution Note
  Note that the ``input_shape`` parameter in the YAML file specifies the input data dimensions of the original floating-point model. For dynamic input models, this parameter can be used to set the input size after conversion. The shape of the calibration data should match the ``input_shape``. For example, if the original floating-point model has an input node shape of ?x3x224x224 (where "?" represents a placeholder, meaning the first dimension is dynamic), and you set ``input_shape: 8x3x224x224`` in the configuration file, then each calibration data sample must have a size of 8x3x224x224. (Note: Models where the first dimension of the input shape is not 1 do not support modifying batch information via the input_batch parameter.)
:::

#### Using the hb_mapper makertbin Tool for Model Conversion {#makertbin}

hb_mapper makertbin offers two modes: with ``fast-perf`` enabled and without ``fast-perf`` enabled.

Enabling ``fast-perf`` mode generates a bin model that can run at peak performance on the board during conversion. The tool primarily performs the following operations internally:

- Runs BPU-executable operators on the BPU whenever possible (for ``RDK X5``, operators can be specified to run on the BPU using the node_info parameter in the YAML file; ``RDK X3`` is auto-optimized and does not support specifying operators via the YAML configuration file).

- Removes non-removable CPU operators at the beginning and end of the model, including Quantize/Dequantize, Transpose, Cast, Reshape, etc.

- Compiles the model with the highest performance optimization level, O3.

:::tip Tip

  It is recommended to refer to the scripts in the D-Robotics model conversion ``horizon_model_convert_sample`` example package for Caffe, ONNX, etc., such as ``03_build_X3.sh``.
:::

The usage of the hb_mapper makertbin command is as follows:

Without enabling ``fast-perf`` mode:

```bash

  hb_mapper makertbin --config ${config_file}  \
                      --model-type  ${model_type}
```

With ``fast-perf`` mode enabled:

```bash

  hb_mapper makertbin --fast-perf --model ${caffe_model/onnx_model} --model-type ${model_type} \
                      --proto ${caffe_proto} \
                      --march ${march}
```

Explanation of hb_mapper makertbin parameters:

--help<br/>
  Displays help information and exits.

-c, --config<br/>
  The configuration file for model compilation, in YAML format with a .yaml suffix. Refer to the following sections for a complete configuration file template.

--model-type<br/>
  Specifies the type of input model for conversion. Currently supports ``caffe`` or ``onnx``.

--fast-perf<br/>
  Enables fast-perf mode. When enabled, this mode generates a bin model that can run at peak performance on the board, facilitating subsequent model performance evaluation.

  If you enable fast-perf mode, the following additional configurations are required:

  --model<br/>
  The Caffe or ONNX floating-point model file.

  --proto<br/>
  Specifies the prototxt file for the Caffe model.

  --march<br/>
  The microarchitecture of the BPU. Set to ``bernoulli2`` for ``RDK X3`` and ``bayes-e`` for ``RDK X5``.

:::caution Note

  - For ``RDK X3 YAML configuration files``, you can directly use the template files [**RDK X3 Caffe model quantization YAML template**](../../../08_FAQ/05_toolchain.md#rdk_x3_caffe_yaml_template) and [**RDK X3 ONNX model quantization YAML template**](../../../08_FAQ/05_toolchain.md#rdk_x3_onnx_yaml_template) to fill in the required information.

  - For ``RDK X5 YAML configuration files``, you can directly use the template files [**RDK X5 Caffe model quantization YAML template**](../../../08_FAQ/05_toolchain.md#rdk_x5_caffe_yaml_template) and [**RDK X5 ONNX model quantization YAML template**](../../../08_FAQ/05_toolchain.md#rdk_x5_onnx_yaml_template) to fill in the required information.

  - If the hb_mapper makertbin step terminates abnormally or reports an error, model conversion has failed. Refer to the error messages printed in the terminal or the log file ``hb_mapper_makertbin.log`` generated in the current directory to identify the error and suggested fixes. Error information can also be found in the [**Model Quantization Errors and Solutions**](../../../08_FAQ/05_toolchain.md#model_convert_errors_and_solutions) section. If the issue persists, contact the D-Robotics technical support team or post your question on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc/). We will provide support within 24 hours.
:::

#### Explanation of YAML Configuration Parameters for Model Conversion {#yaml_config}

:::info Note
  Either a Caffe model or an ONNX model is used, i.e., choose between ``caffe_model`` + ``prototxt`` or ``onnx_model``.
  In other words, either a Caffe model or an ONNX model is used.
:::
```
  # Model parameters group
  model_parameters:
    # Original Caffe floating-point model description file
    prototxt: '***.prototxt'

    # Original Caffe floating-point model data file
    caffe_model: '****.caffemodel'

    # Original ONNX floating-point model file
    onnx_model: '****.onnx'

    # Target processor architecture for conversion, keep default. D-Robotics RDK X3 uses bernoulli2, RDK X5 uses bayes-e. march: 'bayes-e'
    march: 'bernoulli2'

    # Prefix for the output model file name for board execution after conversion
    output_model_file_prefix: 'mobilenetv1'

    # Directory to store the results of model conversion
    working_dir: './model_output_dir'

    # Specifies whether the converted hybrid heterogeneous model retains the ability to output intermediate layer results; keep default
    layer_out_dump: False

    # Specifies the output nodes of the model
    output_nodes: {OP_name}

    # Batch delete nodes of a specific type
    remove_node_type: Dequantize

    # Delete nodes with specified names
    remove_node_name: {OP_name}

  # Input information parameters group
  input_parameters:
    # Name of the input node of the original floating-point model
    input_name: "data"

    # Data format of the original floating-point model's input (quantity/order consistent with input_name)
    input_type_train: 'bgr'

    # Data layout of the original floating-point model's input (quantity/order consistent with input_name)
    input_layout_train: 'NCHW'

    # Dimensions of the original floating-point model's input data
    input_shape: '1x3x224x224'

    # Batch size fed to the network during actual execution; default is 1
    input_batch: 1

    # Preprocessing method added to the model for input data
    norm_type: 'data_mean_and_scale'

    # Mean values subtracted from the image in the preprocessing method; for channel-wise means, values must be separated by spaces
    mean_value: '103.94 116.78 123.68'

    # Scale factor for the image in the preprocessing method; for channel-wise scaling, values must be separated by spaces
    scale_value: '0.017'

    # Input data format that the converted hybrid heterogeneous model needs to adapt to (quantity/order consistent with input_name)
    input_type_rt: 'yuv444'

    # Special format for input data
    input_space_and_range: 'regular'

    # Input data layout that the converted hybrid heterogeneous model needs to adapt to (quantity/order consistent with input_name). Not required if input_type_rt is set to nv12
    input_layout_rt: 'NHWC'

  # Calibration parameters group
  calibration_parameters:
    # Directory containing calibration samples used for model calibration
    cal_data_dir: './calibration_data'

    # Data storage type for calibration binary files
    cal_data_type: 'float32'

    # Enable automatic processing of image calibration samples (skimage read; resize to input node dimensions)
    #preprocess_on: False  
    
    # Calibration algorithm type; prioritize using the default calibration algorithm
    calibration_type: 'default'

    # Parameter for the max calibration method
    # max_percentile: 1.0

    # Force specific operators to run on the CPU; generally not needed, can be enabled during model accuracy tuning for optimization attempts
    #run_on_cpu:  {OP_name}

    # Force specific operators to run on the BPU; generally not needed, can be enabled during model performance tuning for optimization attempts
    # run_on_bpu:  {OP_name}

    # Specify whether to calibrate per channel
    #per_channel: False

    # Specify the data precision of output nodes
    #optimization: set_model_output_int8

  # Compiler parameters group
  compiler_parameters:
    # Compilation strategy selection
    compile_mode: 'latency'

    # Enable debug information during compilation; keep default False
    debug: False

    # Number of cores used for model execution
    core_num: 1

    # Optimization level for model compilation; keep default O3
    optimize_level: 'O3'

    # Specify the data source for the input named 'data'
    #input_source: {"data": "pyramid"}

    # Maximum continuous execution time for each function call of the model
    #max_time_per_fc: 1000

    # Number of processes used during model compilation
    #jobs: 8
	
  # This parameters group is not required and is only used when custom CPU operators are enabled
  #custom_op: 
    # Calibration method for custom operators; register is recommended
    #custom_op_method: register

    # Implementation files for custom operators; multiple files can be separated by ";". These files can be generated from templates. See custom operator documentation for details
    #op_register_files: sample_custom.py

    # Folder containing custom operator implementation files; use relative paths
    #custom_op_dir: ./custom_op
```

The configuration file mainly consists of the model parameters group, input information parameters group, calibration parameters group, and compiler parameters group. All four parameter groups must be present in your configuration file. Specific parameters are either optional or mandatory; optional parameters can be omitted.

Parameters are set in the format: ``param_name: 'param_value'``. If a parameter has multiple values, separate them using the ``';'`` symbol: ``param_name: 'param_value1; param_value2; param_value3'``. Refer to ``run_on_cpu: 'conv_0; conv_1; conv12'`` for an example.

:::tip Tip
  
  - For multi-input models, it is recommended to explicitly specify optional parameters (such as ``input_name``, ``input_shape``, etc.) to avoid order mismatches.

  - When configuring march as bayes-e (i.e., for RDK X5 model conversion) and setting the optimization level to O3, hb_mapper makerbin provides caching capabilities by default. The first time you compile the model using hb_mapper makerbin, a cache file is automatically created. If your working_dir remains unchanged, subsequent compilations will automatically use this cache file, reducing compilation time.
:::

:::caution Note

  - If ``input_type_rt`` is set to ``nv12`` or ``yuv444``, the model's input dimensions must not contain odd numbers.
  - Currently, RDK X3 does not support scenarios where ``input_type_rt`` is set to ``yuv444`` and ``input_layout_rt`` is set to ``NCHW`` simultaneously.
  - If, after successful model conversion, operators that meet the D-Robotics BPU operator constraints still run on the CPU, it is mainly because these operators are passively quantized. For more information on passive quantization, refer to the [**Active and Passive Quantization Logic in the Algorithm Toolchain**](https://developer.d-robotics.cc/forumDetail/118364000835765793) section.
:::

Below are the detailed parameter descriptions, organized according to the order of the parameter groups mentioned above.

- ###### Model Parameters Group

| Parameter Name | Description | Value Range | Optional/Mandatory |
|------------|----------|----------|--------|
|``prototxt``| **Function**: Specifies the name of the prototxt file for the Caffe floating-point model.<br/>**Description**: Required when ``hb_mapper makertbin``'s ``model-type`` is set to ``caffe``.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``caffe_model``| **Function**: Specifies the name of the caffemodel file for the Caffe floating-point model.<br/>**Description**: Required when ``hb_mapper makertbin``'s ``model-type`` is set to ``caffe``.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``onnx_model``| **Function**: Specifies the name of the ONNX file for the ONNX floating-point model.<br/>**Description**: Required when ``hb_mapper makertbin``'s ``model-type`` is set to ``onnx``.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``march``| **Function**: Specifies the platform architecture the output hybrid heterogeneous model needs to support.<br/>**Description**: The two configurable values correspond to the BPU micro-frameworks of RDK X3 and RDK Ultra, respectively. Choose based on your platform.| **Value Range**: ``bernoulli2`` or ``bayes``.<br/> **Default**: None.|Mandatory |
|``output_model_file_prefix``| **Function**: Specifies the prefix for the output hybrid heterogeneous model name.<br/>**Description**: The prefix for the name of the fixed-point model file output.| **Value Range**: None.<br/> **Default**: None.|Mandatory |
|``working_dir``| **Function**: Specifies the directory where the model conversion results are stored.<br/>**Description**: If the directory does not exist, the tool automatically creates it.| **Value Range**: None.<br/> **Default**: ``model_output``.|Optional |
|``layer_out_dump``| **Function**: Specifies whether the hybrid heterogeneous model retains the ability to output intermediate layer values.<br/>**Description**: Outputting intermediate layer values is a debugging feature; do not enable it under normal circumstances.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |
|``output_nodes``| **Function**: Specifies the output nodes of the model.<br/>**Description**: Typically, the conversion tool automatically identifies the model's output nodes. This parameter allows you to specify certain intermediate layers as outputs. Set the value to specific node names in the model. Refer to the earlier description of ``param_value`` for configuring multiple values. Note that once set, the tool no longer automatically identifies output nodes; the nodes you specify become the only outputs.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``remove_node_type``| **Function**: Sets the types of nodes to delete.<br/>**Description**: This is a hidden parameter; leaving it unset or empty does not affect the model conversion process. It allows you to specify the types of nodes to delete. The nodes to be deleted must be at the beginning or end of the model, connected to the input or output. Note that nodes are deleted sequentially, and the model structure is updated dynamically. Before deletion, it is checked whether the node is at the input or output of the model. Therefore, the deletion order is important.| **Value Range**: "Quantize", "Transpose", "Dequantize", "Cast", "Reshape". Separate different types with ";".<br/> **Default**: None.|Optional |
|``remove_node_name``| **Function**: Sets the names of nodes to delete.<br/>**Description**: This is a hidden parameter; leaving it unset or empty does not affect the model conversion process. It allows you to specify the names of nodes to delete. The nodes to be deleted must be at the beginning or end of the model, connected to the input or output. Note that nodes are deleted sequentially, and the model structure is updated dynamically. Before deletion, it is checked whether the node is at the input or output of the model. Therefore, the deletion order is important.| **Value Range**: None. Separate different types with ";".<br/> **Default**: None.|Optional |
|``set_node_data_type``| **Function**: Configures the output data type of specified ops as int16. **This parameter is only supported for RDK Ultra and RDK X5!** <br/> **Description**: During model conversion, the default input and output data type for most ops is int8. This parameter allows you to specify the output data type of certain ops as int16 (subject to certain constraints). For details on int16, refer to the [**int16 Configuration**](#int16_config) section. <br/> **Note:** The functionality of this parameter has been merged into the ``node_info`` parameter and is planned for deprecation in future versions. | **Value Range**: Refer to the operator support constraint list for RDK Ultra and RDK X5 in the [**Model Operator Support List**](./supported_op_list).<br/> **Default**: None.|Optional |
|``debug_mode``| **Function**: Saves calibration data for accuracy debugging analysis.<br/>**Description**: This parameter saves calibration data in .npy format for accuracy debugging. The data can be loaded using np.load() and fed directly into the model for inference. If this parameter is not set, you can also save the data manually and use accuracy debugging tools for analysis. | **Value Range**: ``"dump_calibration_data"``<br/> **Default**: None.|Optional |
|``node_info``| **Function**: Supports configuring the input/output data types of specified ops as int16 and forcing specific operators to run on the CPU or BPU. **This parameter is only supported for RDK Ultra and RDK X5!** <br/>**Description**: To reduce the number of parameters in the YAML file, we have merged the capabilities of the ``set_node_data_type``, ``run_on_cpu``, and ``run_on_bpu`` parameters into this parameter, and further expanded support to configure the input data type of specified ops as int16.<br/> Usage of the ``node_info`` parameter: <br/>- Specifying only that an op runs on the BPU/CPU (using BPU as an example; the method for CPU is similar):<br/> node_info:<br/> `{ "node_name" { 'ON': 'BPU',} }` <br/>- Specifying that an op runs on the BPU while also configuring its input/output data types:<br/> node_info:<br/> `{ "node_name": { 'ON': 'BPU', 'InputType': 'int16', 'OutputType': 'int16'}} ` <br/>- Specifying multiple operators to run:<br/> node_info:<br/>`{"/model.0/conv/Conv": {"ON": "BPU","InputType": "int16","OutputType": "int16"},`<br/>`"/model.0/act/Mul": {"ON": "BPU","InputType": "int16","OutputType": "int16"},`<br/>`"/model.2/Concat": {"ON": "BPU","InputType": "int16","OutputType": "int16"}}`
'InputType': 'int16' specifies that all input data types of the operator are int16. <br/>To specify the InputType for a particular input of an operator, you can append a number to InputType. For example:<br/>'InputType0': 'int16' specifies that the first input data type of the operator is int16,<br/>'InputType1': 'int16' specifies that the second input data type of the operator is int16, and so on.<br/>**Note:** 'OutputType' does not support specifying OutputType for a particular output of an operator. Configuration applies to all outputs of the operator. Configurations like 'OutputType0' or 'OutputType1' are not supported. | **Value Range**: Refer to the operator support constraint list for RDK Ultra and RDK X5 in the [Model Operator Support List](./supported_op_list). Operators that can be specified to run on CPU or BPU must be present in the model.<br/> **Default**: None.|Optional |

- ###### Input Information Parameters Group

| Parameter Name | Description | Value Range | Optional/Mandatory |
|------------|----------|----------|--------|
|``input_name``| **Function**: Specifies the name of the input node of the original floating-point model.<br/>**Description**: Not required if the floating-point model has only one input node. Must be configured when there is more than one input node to ensure the accuracy of subsequent type and calibration data input order. Refer to the earlier description of param_value for configuring multiple values.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``input_type_train``| **Function**: Specifies the input data type of the original floating-point model.<br/>**Description**: Each input node needs to be configured with a specific input data type. When there are multiple input nodes, the order of the set values must strictly match the order in ``input_name``. Refer to the earlier description of ``param_value`` for configuring multiple values. For information on data type selection, refer to the "Interpretation of Internal Conversion Process" section.| **Value Range**: ``rgb``, ``bgr``, ``yuv444``, ``gray``, ``featuremap``.<br/> **Default**: None.|Mandatory |
|``input_layout_train``| **Function**: Specifies the input data layout of the original floating-point model.<br/>**Description**: Each input node needs to be configured with a specific input data layout, which must match the data layout used by the original floating-point model. When there are multiple input nodes, the order of the set values must strictly match the order in ``input_name``. Refer to the earlier description of ``param_value`` for configuring multiple values. For information on data layout, refer to the "Interpretation of Internal Conversion Process" section.| **Value Range**: NHWC, NCHW.<br/> **Default**: None.|Mandatory |
|``input_type_rt``| **Function**: The input data format that the converted hybrid heterogeneous model needs to adapt to.<br/>**Description**: This specifies the data format you intend to use. It does not need to match the data format of the original model, but note that the data fed to the model on the platform must use this format. Each input node needs to be configured with a specific input data type. When there are multiple input nodes, the order of the set values must strictly match the order in ``input_name``. Refer to the earlier description of ``param_value`` for configuring multiple values. For information on data type selection, refer to the "Interpretation of Internal Conversion Process" section.| **Value Range**: ``rgb``, ``bgr``, ``yuv444``, ``nv12``, ``gray``, ``featuremap``.<br/> **Default**: None.|Mandatory |
|``input_layout_rt``| **Function**: The input data layout that the converted hybrid heterogeneous model needs to adapt to.<br/>**Description**: Each input node needs to be configured with a specific input data layout, which is the layout you want to assign to the hybrid heterogeneous model. Inappropriate layout settings may affect performance. For the X3 platform, it is recommended to use the NHWC format. If input_type_rt is set to nv12, this parameter is not required. When there are multiple input nodes, the order of the set values must strictly match the order in ``input_name``. Refer to the earlier description of ``param_value`` for configuring multiple values. For information on data layout, refer to the "Interpretation of Internal Conversion Process" section.| **Value Range**: ``NCHW``, ``NHWC``.<br/> **Default**: None.|Optional |
|``input_space_and_range``| **Function**: Specifies the special format for input data.<br/>**Description**: This parameter is used to adapt to different yuv420 formats output by the ISP. It is only effective when input_type_rt is set to nv12. 'regular' represents the common yuv420 format with a value range of [0,255]; 'bt601_video' is another video standard yuv420 format with a value range of [16,235]. For more information, refer to online resources about bt601. Do not configure this parameter unless explicitly needed.| **Value Range**: ``regular``, ``bt601_video``.<br/> **Default**: ``regular``.|Optional |
|``input_shape``| **Function**: Specifies the input data dimensions of the original floating-point model.<br/>**Description**: Dimensions are concatenated with 'x', e.g., 1x3x224x224. Not required if the original floating-point model has only one input node, as the tool automatically reads the dimension information from the model file. When configuring multiple input nodes, the order of the set values must strictly match the order in ``input_name``. Refer to the earlier description of ``param_value`` for configuring multiple values.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``input_batch``| **Function**: Specifies the input batch size that the converted hybrid heterogeneous model needs to adapt to.<br/>**Description**: This input_batch refers to the batch size for the converted hybrid heterogeneous bin model's input but does not affect the batch size of the converted ONNX model's input. Defaults to 1 if not set. This parameter is only applicable to single-input models, and the first dimension of ``input_shape`` must be 1.| **Value Range**: ``1-128``.<br/> **Default**: ``1``.|Optional |
|``norm_type``| **Function**: The input data preprocessing method added to the model.<br/>**Description**: ``no_preprocess`` means no data preprocessing is added; ``data_mean`` means mean subtraction preprocessing is added; ``data_scale`` means scale factor multiplication preprocessing is added; ``data_mean_and_scale`` means mean subtraction followed by scale factor multiplication preprocessing is added. When there is more than one input node, the order of the set values must strictly match the order in ``input_name``. Refer to the earlier description of ``param_value`` for configuring multiple values. For the impact of configuring this parameter, refer to the "Interpretation of Internal Conversion Process" section.|**Value Range**: ``data_mean_and_scale``, ``data_mean``, ``data_scale``, ``no_preprocess``.<br/> **Default**: None.|Mandatory |
|``mean_value``| **Function**: Specifies the mean values subtracted from the image in the preprocessing method.<br/>**Description**: Required when ``norm_type`` is set to ``data_mean_and_scale`` or ``data_mean``. For each input node, there are two configuration methods. The first is to configure a single value, indicating that this mean is subtracted from all channels. The second is to provide a number of values equal to the number of channels (values separated by spaces), indicating that different means are subtracted from each channel. The number of configured input nodes must match the number of nodes configured in ``norm_type``. If a node does not require mean subtraction, configure it as ``'None'``. Refer to the earlier description of ``param_value`` for configuring multiple values.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``scale_value``| **Function**: Specifies the scale factor for the data in the preprocessing method.<br/>**Description**: Required when ``norm_type`` is set to ``data_mean_and_scale`` or ``data_scale``. For each input node, there are two configuration methods. The first is to configure a single value, indicating that all channels are multiplied by this factor. The second is to provide a number of values equal to the number of channels (values separated by spaces), indicating that different channels are multiplied by different factors. The number of configured input nodes must match the number of nodes configured in ``norm_type``. If a node does not require scaling, configure it as ``'None'``. Refer to the earlier description of ``param_value`` for configuring multiple values.| **Value Range**: None.<br/> **Default**: None.|Optional |

**Additional Notes on input_type_rt/input_type_train**

The computational platform architecture of RDK X5 makes two assumptions to improve performance:

1. It assumes that the input data is quantized int8 data.

2. It assumes that the data obtained from the camera is nv12.

Therefore, if you use rgb (NCHW) input format during model training but want the model to efficiently handle nv12 data, simply configure the following during model conversion:

```bash
  input_parameters:
      input_type_rt: 'nv12'
      input_type_train: 'rgb'
      input_layout_train: 'NCHW'
```

**Tip:**
- If you use the gray format during model training but the actual input data format is nv12, you can configure both ``input_type_rt`` and ``input_type_train`` as ``gray`` in the model conversion, and during embedded application development, simply use the y-channel address of nv12 as input.

- ###### Calibration Parameters Group

| Parameter Name | Description | Value Range | Optional/Mandatory |
|------------|----------|----------|--------|
|``cal_data_dir``| **Function**: Specifies the directory containing the calibration samples used for model calibration.<br/>**Description**: The calibration data in the directory must meet the input configuration requirements. Refer to the "Preparing Calibration Data" section for details. When configuring multiple input nodes, the order of the set values must strictly match the order in ``input_name``. Refer to the earlier description of ``param_value`` for configuring multiple values. When calibration_type is set to ``load`` or ``skip``, cal_data_dir is not required. Note: For convenience, if cal_data_type configuration is not found, the data type is determined based on the folder suffix. If the folder suffix ends with ``_f32``, the data type is considered float32; otherwise, it is considered uint8. However, we strongly recommend explicitly specifying the data type using the cal_data_type parameter.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``cal_data_type``| **Function**: Specifies the data storage type for the calibration binary files.<br/>**Description**: Specifies the data storage type of the binary files used for model calibration. If not specified, it will be determined using the folder name suffix.| **Value Range**: ``float32``, ``uint8``.<br/> **Default**: None.|Optional |
|``preprocess_on``| **Function**: Enables automatic processing of image calibration samples.<br/>**Description**: This option is only applicable to models with 4-dimensional image inputs. Do not enable it for non-4D models. When this feature is enabled, the cal_data_dir directory should contain image data such as jpg, bmp, png. The tool reads the images using skimage and resizes them to the dimensions required by the input node. To ensure calibration quality, it is recommended to keep this parameter disabled. For the impact of using this feature, refer to the "Preparing Calibration Data" section.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |
|``calibration_type``| **Function**: The calibration algorithm type.<br/>**Description**: Both ``kl`` and ``max`` are well-known calibration quantization algorithms. Their basic principles can be found in online resources. When using the ``load`` method for calibration, the QAT model must be exported via a plugin. ``mix`` is a search strategy that integrates multiple calibration methods. It automatically identifies quantization-sensitive nodes and selects the best method from different calibration approaches at the node granularity, ultimately constructing a combined calibration method that leverages the strengths of various methods. ``default`` is an automatic search strategy that attempts to find a combination of calibration quantization parameters that yields relatively good results. It is recommended to first try ``default``. If the final accuracy does not meet expectations, adjust the calibration parameters according to the suggestions in the accuracy tuning section. If you only want to verify the model's performance without requiring high accuracy, you can try the ``skip`` method. This method uses random numbers for calibration and does not require preparing calibration data. It is suitable for initial attempts to verify the model structure. Note: When using the skip method, the resulting model uses random numbers for calibration and cannot be used for accuracy validation.| **Value Range**: ``default``, ``mix`, ``kl``, ``max``, ``load``, and ``skip``.<br/> **Default**: ``default``.|Mandatory |
|``max_percentile``| **Function**: This parameter is for the ``max`` calibration method, used to adjust the clipping point for max calibration.<br/>**Description**: This parameter is only effective when ``calibration_type`` is set to ``max``. Common configuration options include: 0.99999/0.99995/0.99990/0.99950/0.99900. It is recommended to first try configuring ``calibration_type`` as ``default``. If the final accuracy does not meet expectations, adjust this parameter according to the suggestions in the accuracy tuning section.| **Value Range**: ``0.0`` to ``1.0``.<br/> **Default**: ``1.0``.|Optional |
|``per_channel``| **Function**: Controls whether to calibrate each channel of the feature map.<br/>**Description**: Effective when ``calibration_type`` is set to a value other than default. It is recommended to first try ``default``. If the final accuracy does not meet expectations, adjust this parameter according to the suggestions in the accuracy tuning section.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |
|``run_on_cpu``| **Function**: Forces specified operators to run on the CPU.<br/>**Description**: While the CPU may not perform as well as the BPU, it provides float precision computation. If you are certain that certain operators need to run on the CPU, you can specify them using this parameter. Set the value to the specific node names in the model. Refer to the earlier description of ``param_value`` for configuring multiple values.<br/> **Note:** The functionality of this parameter has been merged into the ``node_info`` parameter for **RDK Ultra and RDK X5** and is planned for deprecation in future versions. **RDK X3** continues to use it. | **Value Range**: None.<br/> **Default**: None.|Optional |
|``run_on_bpu``| **Function**: Forces specified operators to run on the BPU.<br/>**Description**: In rare cases, to ensure the accuracy of the final quantized model, the conversion tool may place some operators that are capable of running on the BPU onto the CPU. If you have high performance requirements and are willing to accept some quantization loss, you can explicitly specify operators to run on the BPU using this parameter. Set the value to the specific node names in the model. Refer to the earlier description of ``param_value`` for configuring multiple values.<br/> **Note:** The functionality of this parameter has been merged into the ``node_info`` parameter for **RDK Ultra and RDK X5** and is planned for deprecation in future versions. **RDK X3** continues to use it.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``optimization``| **Function**: Outputs the model in int8/int16 format.<br/>**Description**: When set to set_model_output_int8, the model is output in low-precision int8 format; when set to set_model_output_int16, the model is output in low-precision int16 format.<br/> **Note:** **RDK X3** only supports setting set_model_output_int8. <br/>**RDK Ultra and RDK X5** support setting either set_model_output_int8 or set_model_output_int16.|**Value Range**: ``set_model_output_int8`` or ``set_model_output_int16``.<br/> **Default**: None.|Optional |

- ###### Compiler Parameters Group

| Parameter Name | Description | Value Range | Optional/Mandatory |
|------------|----------|----------|--------|
|``compile_mode``| **Function**: Compilation strategy selection.<br/>**Description**: ``latency`` aims to optimize inference time; ``bandwidth`` aims to optimize DDR access bandwidth. If the model does not significantly exceed the expected bandwidth usage, it is recommended to use the ``latency`` strategy.| **Value Range**: ``latency``, ``bandwidth``.<br/> **Default**: ``latency``.|Mandatory |
|``debug``| **Function**: Whether to enable debug information during compilation.<br/>**Description**: When this parameter is enabled, static performance analysis results of the model are saved in the model. You can view the performance information of BPU operators layer by layer (including computation amount, computation time, and data transfer time) in the Layer Details tab of the static performance evaluation HTML page generated after successful model conversion and the HTML page generated during hb_perf. By default, it is recommended to keep this parameter disabled.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |
|``core_num``| **Function**: Number of cores used for model execution.<br/>**Description**: The D-Robotics platform supports using multiple AI accelerator cores simultaneously to complete an inference task. Multi-core is suitable for large input sizes, and ideally, dual-core speed can reach about 1.5 times that of a single core. If your model has a large input size and you have high performance requirements, you can configure ``core_num=2``.<br/> **Note:** This option is not yet supported for **RDK Ultra and RDK X5**. The default configuration is 1; please do not configure it! | **Value Range**: ``1``, ``2``.<br/> **Default**: ``1``.|Optional |=
|``optimize_level``| **Function**: Optimization level selection for model compilation.<br/>**Description**: The optimization level ranges from ``O0`` to ``O3``. ``O0`` performs no optimization, with the fastest compilation speed and the lowest level of optimization. As the optimization level increases from ``O1`` to ``O3``, the compiled model is expected to execute faster, but compilation time also increases. To generate and verify model performance, the ``O3`` level optimization must be used to ensure optimal performance. During certain process validation or accuracy debugging, lower optimization levels can be tried to speed up the process.| **Value Range**: ``O0``, ``O1``, ``O2``, ``O3``.<br/> **Default**: None.|Mandatory |
|``input_source``| **Function**: Sets the input data source for the board-running bin model.<br/>**Description**: This parameter is an option for adapting to the engineering environment. It is recommended to configure it only after completing model validation. ``ddr`` indicates that the data comes from memory; ``pyramid`` and ``resizer`` indicate that it comes from fixed hardware on the processor. Note: If set to resizer, the model's h*w must be less than 18432. For specific details on adapting to the engineering environment for ``pyramid`` and ``resizer`` data sources, this parameter configuration is somewhat special. For example, if the model's input name is data and the data source is memory (ddr), the configuration value should be ``{"data": "ddr"}``.| **Value Range**: ``ddr``, ``pyramid``, ``resizer``<br/> **Default**: None; automatically selected from the optional range based on the value of input_type_rt by default.|Optional |
|``max_time_per_fc``| **Function**: Specifies the maximum continuous execution time (in microseconds) for each function call of the model.<br/>**Description**: When the compiled data instruction model performs inference on the BPU, it will be represented as one or more function calls (the execution granularity of the BPU). A value of 0 indicates no restriction. This parameter limits the maximum execution time of each function call. The model can only be preempted after a single function call is completed. For details, refer to the "Model Priority Control" section. - This parameter is only used to implement model preemption functionality. If such functionality is not needed, it can be ignored.<br/> - Model preemption functionality is only supported on the development board, not on the PC-side emulator.| **Value Range**: ``0 or 1000-4294967295``.<br/> **Default**: ``0``.|Optional |
|``jobs``| **Function**: Sets the number of processes when compiling the bin model.<br/>**Description**: Used to set the number of processes when compiling the bin model. Can increase compilation speed to some extent.| **Value Range**: ``Within the range of maximum cores supported by the machine.``<br/> **Default**: None.|Optional |

- ###### Custom Operator Parameters Group

| Parameter Name | Description | Value Range | Optional/Mandatory |
|------------|----------|----------|--------|
|``custom_op_method``| **Function**: Custom operator strategy selection.<br/>**Description**: Currently, only the register strategy is supported.| **Value Range**: ``register``.<br/> **Default**: None.|Optional |
|``op_register_files``| **Function**: Names of the Python implementation files for custom operators.<br/>**Description**: Multiple files can be separated by ``;``| **Value Range**: None.<br/> **Default**: None.|Optional |
|``custom_op_dir``| **Function**: Path to the directory containing the Python implementation files for custom operators.<br/>**Description**: Use relative paths when setting this parameter.| **Value Range**: None.<br/> **Default**: None.|Optional |

##### RDK Ultra and RDK X5 int16 Configuration {#int16_config}
  
During model conversion, most operators in the model are quantized to int8 for computation. By configuring the ``node_info`` parameter, you can specify the input/output data types of a specific op to be int16 (for the specific range of operators supported, refer to the RDK Ultra and RDK X5 operator support list in the [**Model Operator Support List**](./supported_op_list) section). The basic principle is as follows:

After you configure the input/output data type of an op to be int16, the model conversion tool internally automatically updates and checks the int16 configuration of the op's input/output context. For example, when configuring op_1's input/output data type as int16, it potentially simultaneously specifies that the preceding/succeeding op of op_1 also needs to support int16 computation. For unsupported scenarios, the model conversion tool prints a log indicating that the int16 configuration combination is not yet supported and falls back to int8 computation.

##### Preprocessing HzPreprocess Operator Description {#pre_process}
The preprocessing HzPreprocess operator is a preprocessing operator node generated by the D-Robotics model conversion tool during the model conversion process, inserted after the model's input node. It is used to normalize the model's input data. This section mainly describes the ``norm_type``, ``mean_value``, and ``scale_value`` parameter variables and the generation of the model preprocessing HzPreprocess operator node.

**norm_type Parameter Description**

- Function: This parameter specifies the input data preprocessing method added to the model.

- Value Range and Description:

  - ``no_preprocess`` indicates that no data preprocessing is added.
  - ``data_mean`` indicates that mean subtraction preprocessing is added.
  - ``data_scale`` indicates that scale factor multiplication preprocessing is added.
  - ``data_mean_and_scale`` indicates that mean subtraction followed by scale factor multiplication preprocessing is added.

:::caution Note
  When there is more than one input node, the order of the set values must strictly match the order in ``input_name``.
:::

**mean_value Parameter Description**

- Function: This parameter specifies the mean values subtracted from the image in the preprocessing method.

- Usage: Required when ``norm_type`` is set to ``data_mean_and_scale`` or ``data_mean``.

- Description:

  - When there is only one input node, configure a single value, indicating that this mean is subtracted from all channels.
  - When there are multiple nodes, provide a number of values equal to the number of channels (values separated by spaces), indicating that different means are subtracted from each channel.

:::caution Note

  1. The number of configured input nodes must match the number of nodes configured in ``norm_type``.
  2. If a node does not require mean subtraction, configure it as ``'None'``.
:::

**scale_value Parameter Description**

- Function: This parameter specifies the scale factor for the data in the preprocessing method.

- Usage: Required when ``norm_type`` is set to ``data_mean_and_scale`` or ``data_scale``.

- Description:

  - When there is only one input node, configure a single value, indicating that all channels are multiplied by this factor.
  - When there are multiple nodes, provide a number of values equal to the number of channels (values separated by spaces), indicating that different channels are multiplied by different factors.

:::caution Note

  1. The number of configured input nodes must match the number of nodes configured in ``norm_type``.
  2. If a node does not require scaling, configure it as ``'None'``.
:::

**Calculation Formulas and Example**

- Data Standardization Calculation Formula During Model Training

The mean and scale parameters in the YAML file need to be converted from the mean and std used during training.

The calculation method for data standardization in the preprocessing node (i.e., the formula in the HzPreprocess node) is: `norm\_data = ( data − mean ) * scale`.

Take YOLOv3 as an example; the preprocessing code during training is:

```python
def base_transform(image, size, mean, std):
    x = cv2.resize(image, (size, size).astype(np.float32))
    x /= 255
    x -= mean
    x /= std
    return x

class BaseTransform:
    def __init__(self, size, mean=(0.406, 0.456, 0.485), std=(0.225, 0.224, 0.229)):
        self.size = size
        self.mean = np.array(mean, dtype=np.float32)
        self.std = np.array(std, dtype=np.float32)
```

The calculation formula is: `norm\_data= (\frac{data}{255}  −𝑚𝑒𝑎𝑛) * \frac{1}{𝑠𝑡𝑑}`,

Rewriting it as the calculation method of the HzPreprocess node: `norm\_data= (\frac{data}{255}  −𝑚𝑒𝑎𝑛) * \frac{1}{𝑠𝑡𝑑} =(data−255𝑚𝑒𝑎𝑛) * \frac{1}{255𝑠𝑡𝑑}`,

Therefore: `mean\_yaml = 255 mean`, `𝑠𝑐𝑎𝑙𝑒\_𝑦𝑎𝑚𝑙=  \frac{1}{255 𝑠𝑡𝑑}`.

- Calculation Formula During Model Inference

Whether to add the HzPreprocess node depends on the configuration parameters in the YAML file.
When mean/scale are configured, a HzPreprocess node is added to the input during model conversion. The HzPreprocess node can be understood as performing a convolution operation on the input data.

The calculation formula inside HzPreprocess is: `((input (range [-128,127]) + 128) - mean) * scale`, where `weight=scale`, `bias=(128-mean) * scale`.

:::caution Note

  1. After adding mean/scale in the YAML file, there is no need to add MeanTransformer and ScaleTransformer in the preprocessing.
  2. Adding mean/scale in the YAML file includes the parameters in the HzPreprocess node, which is a BPU node.
:::

#### Interpretation of Internal Conversion Process {#conversion_interpretation}

The model conversion phase completes the transformation from a floating-point model to a D-Robotics hybrid heterogeneous model. To enable this heterogeneous model to run quickly and efficiently on the embedded side, model conversion focuses on addressing two main issues: **input data processing** and **model optimization compilation**. This section will elaborate on these two key issues.

**Input Data Processing** The D-Robotics X3 processor provides hardware-level support for certain types of model input paths. For example, the video processing subsystem in the video path provides image cropping, scaling, and other image quality optimization functions for image capture. The output of these subsystems is YUV420 NV12 format images, whereas algorithmic models are often trained based on common image formats like bgr/rgb.

D-Robotics provides the following solutions for this situation:

- 1. Each converted model has two descriptions: one describes the input data of the original floating-point model (``input_type_train`` and ``input_layout_train``), and the other describes the input data of the processor we need to interface with (``input_type_rt`` and ``input_layout_rt``).

- 2. Image data mean/scale operations are also common, but data formats supported by processors like YUV420 NV12 are not suitable for such operations. Therefore, we have also embedded these common image pre-processing steps into the model.

After processing in the above two ways, the input part of the ``***.bin`` heterogeneous model produced in the model conversion phase becomes as shown in the figure below.

![input_data_process](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/input_data_process.png)

The data layouts in the above figure are only NCHW and NHWC, where N represents the number, C represents the channel, H represents the height, and W represents the width. These two different layouts reflect different memory access characteristics. NHWC is more commonly used in TensorFlow models, while NCHW is used in Caffe. The D-Robotics processor does not restrict the data layout used, but there are two requirements: first, ``input_layout_train`` must be consistent with the data layout of the original model; second, data with a layout consistent with ``input_layout_rt`` must be prepared on the processor. The correct data layout is the basis for successfully parsing the data.

The model conversion tool automatically adds data conversion nodes based on the data formats specified by ``input_type_rt`` and ``input_type_train``. Based on D-Robotics' practical experience, not all type combinations are needed. To avoid misuse, we only open up some fixed type combinations, as shown in the table below:

  | ``input_type_train`` \\ ``input_type_rt`` | nv12 | yuv444 | rgb | bgr | gray | featuremap |
  |-------|------|--------|-----|-----|------|------------|
  | yuv444                                    | Y    | Y      | N   | N   | N    | N          |
  | rgb                                       | Y    | Y      | Y   | Y   | N    | N          |
  | bgr                                       | Y    | Y      | Y   | Y   | N    | N          |
  | gray                                      | N    | N      | N   | N   | Y    | N          |
  | featuremap                                | N    | N      | N   | N   | N    | Y          |
:::info Note

  The first row of the table lists the types supported in ``input_type_rt``, and the first column lists the types supported in ``input_type_train``. **Y/N** indicates whether the conversion from the corresponding ``input_type_rt`` to ``input_type_train`` is supported. In the final output bin model obtained from model conversion, the conversion from ``input_type_rt`` to ``input_type_train`` is an internal process. You only need to pay attention to the data format of ``input_type_rt``. **Correctly understanding the requirements for each** ``input_type_rt`` **is very important for preparing inference data for embedded applications. The following is an explanation of each** ``input_type_rt`` **format:**

  - rgb, bgr, and gray are common image formats. Note that each value is represented by UINT8.
  - yuv444 is a common image format. Note that each value is represented by UINT8.
  - nv12 is a common yuv420 image format. Each value is represented by UINT8.
  - A special case for nv12 is when ``input_space_and_range`` is set to ``bt601_video`` (refer to the previous description of the ``input_space_and_range`` parameter). Compared to the regular nv12 case, its value range changes from [0,255] to [16,235], but each value is still represented by UINT8.
  - For featuremap input models, the data format type only requires that your data be four-dimensional, with each value represented by float32. For example, radar and speech models often use this format.
:::

:::tip Tip

  The calibration data only needs to be processed to input_type_train, and also be careful **not to perform duplicate norm operations**.

  The above ``input_type_rt`` and ``input_type_train`` are fixed in the processing flow of the algorithm toolchain. If you are very sure that conversion is not needed, you can set both ``input_type`` parameters to the same configuration. In this case, ``input_type`` will be processed as a passthrough, and it will not affect the actual execution performance of the model.

  Similarly, data preprocessing is also fixed in the flow. If you do not need any preprocessing, you can disable this function through the ``norm_type`` configuration, and it will not affect the actual execution performance of the model.
:::

**Model Optimization Compilation** It completes several important stages: model parsing, model optimization, model calibration and quantization, and model compilation. Its internal working process is shown in the figure below.

![model_optimization](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/model_optimization.png)

:::info Note

  1. ``input_type_rt*`` represents the intermediate format of input_type_rt.
  
  2. The X3 processor architecture only supports reasoning on ``NHWC`` data. Please use the visualization tool Netron to view the data layout of the input node of the ``quantized_model.onnx`` file to decide whether to add a ``layout conversion`` in the preprocessing.
:::

**Model Parsing Stage** For Caffe floating-point models, it completes the conversion to ONNX floating-point models. Based on the configuration parameters in the conversion YAML file, it decides whether to add a data preprocessing node to the original floating-point model. This stage produces an original_float_model.onnx. The computation precision of this ONNX model is still float32, but a data preprocessing node is added to the input part.

Ideally, this preprocessing node should complete the full conversion from ``input_type_rt`` to ``input_type_train``. However, in reality, the entire type conversion process is completed in coordination with the D-Robotics processor hardware, and the ONNX model does not include the hardware conversion part. Therefore, the actual input type of the ONNX model uses an intermediate type, which is the result type of the hardware processing of ``input_type_rt``. The data layout (NCHW/NHWC) remains consistent with the input layout of the original floating-point model. Each ``input_type_rt`` has a specific corresponding intermediate type, as shown in the following table:

  | **nv12**   | **yuv444** | **rgb** | **bgr** | **gray** | featuremap |
  |------------|------------|---------|---------|----------|------------|
  | yuv444_128 | yuv444_128 | RGB_128 | BGR_128 | GRAY_128 | featuremap |

:::info Note

  The bold parts in the first row of the table are the data types specified by ``input_type_rt``, and the second row is the intermediate type corresponding to the specific ``input_type_rt``. This intermediate type is the input type of original_float_model.onnx. Each type is explained below:

  - yuv444_128 is the result of subtracting 128 from yuv444 data, with each value represented by int8.
  - RGB_128 is the result of subtracting 128 from RGB data, with each value represented by int8.
  - BGR_128 is the result of subtracting 128 from BGR data, with each value represented by int8.
  - GRAY_128 is the result of subtracting 128 from gray data, with each value represented by int8.
  - featuremap is a four-dimensional tensor data, with each value represented by float32.
:::

**Model Optimization Stage** Implements some operator optimization strategies suitable for the D-Robotics platform, such as BN fusion into Conv. The output of this stage is an optimized_float_model.onnx. The computation precision of this ONNX model is still float32, and the optimization does not affect the model's calculation results. The input data requirements for the model remain the same as the previous original_float_model.

**Model Calibration Stage** Uses the calibration data you provide to calculate necessary quantization threshold parameters. These parameters are directly input into the quantization stage and do not produce a new model state.

**Model Quantization Stage** Uses the parameters obtained from calibration to complete model quantization. The output of this stage is a quantized_model.onnx. The computation precision of this model is already int8. This model can be used to evaluate the accuracy loss caused by model quantization. The basic data format and layout required for input are still the same as those of the ``original_float_model``, but the layout and numerical representation have changed. The overall changes compared to the input of the ``original_float_model`` are described as follows:

- For ``RDK X3``, the data layout is always NHWC.
- When the value of ``input_type_rt`` is not ``featuremap``, the input data type is always INT8. Conversely, when ``input_type_rt`` is set to ``featuremap``, the input data type is float32.

The relationship of data layout is as follows:

- Original model input layout: NCHW.
- input_layout_train: NCHW.
- origin.onnx input layout: NCHW.
- calibrated_model.onnx input layout: NCHW.
- quanti.onnx input layout: NHWC.

That is, the input layout of input_layout_train, origin.onnx, and calibrated_model.onnx is consistent with the input layout of the original model.

:::caution Note
  Please note that if input_type_rt is nv12, the input layout of the corresponding quanti.onnx is always NHWC.
:::

**Model Compilation Stage** Uses the D-Robotics model compiler to convert the quantized model into computation instructions and data supported by the D-Robotics platform. The output of this stage is a ``***.bin`` model. This bin model is the model that can run on the D-Robotics embedded platform and is the final output of model conversion.

#### Interpretation of Conversion Results
This section will sequentially introduce the interpretation of successful model conversion status and analysis methods for unsuccessful conversion.
To confirm successful model conversion, you need to verify three aspects: the status information from ``makertbin``, similarity information, and the output in the `working_dir` directory.
Regarding the status information from ``makertbin``, upon successful conversion, a clear prompt message will be given at the end of the console output, as follows:

```bash
  2021-04-21 11:13:08,337 INFO Convert to runtime bin file successfully!
  2021-04-21 11:13:08,337 INFO End Model Convert
```
Similarity information also exists in the console output of ``makertbin``, preceding the ``makertbin`` status information. Its content appears as follows:

```bash
  ======================================================================
  Node    ON   Subgraph  Type     Cosine Similarity  Threshold
  ```bash
  ...    ...     ...     ...       0.999936           127.000000
  ...    ...     ...     ...       0.999868           2.557209
  ...    ...     ...     ...       0.999268           2.133924
  ...    ...     ...     ...       0.996023           3.251645
  ...    ...     ...     ...       0.996656           4.495638
```

In the output content listed above, the columns Node, ON, Subgraph, and Type are interpreted consistently with the ``hb_mapper checker`` tool. Please refer to the earlier section [**Interpreting Check Results**](#check_result). Threshold is the calibration threshold for each layer, used to provide feedback to D-Robotics technical support in abnormal situations; it does not require attention under normal circumstances. The Cosine Similarity column reflects the cosine similarity between the output results of the corresponding operator in the original floating-point model and the quantized model.

:::tip Tip

  In general, **a Cosine Similarity >= 0.99 for the model's output nodes indicates that the model quantization is normal**. A similarity below 0.8 for the output nodes indicates significant accuracy loss. Of course, Cosine Similarity is just a reference method to indicate the stability of data after quantization. There is no obvious direct relationship with the impact on model accuracy. For a completely accurate assessment of accuracy, please refer to the [**Model Accuracy Analysis and Tuning**](#accuracy_evaluation) section.
:::

The conversion outputs are stored in the path specified by the conversion configuration parameter ``working_dir``. After successful model conversion, you will find the following files in this directory (the ``***`` part is what you specified via the conversion configuration parameter ``output_model_file_prefix``):

- \*\*\*_original_float_model.onnx
- \*\*\*_optimized_float_model.onnx
- \*\*\*_calibrated_model.onnx
- \*\*\*_quantized_model.onnx
- \*\*\*.bin

[**Interpreting Conversion Outputs**](#conversion_output) introduces the purpose of each output.

:::caution Note
  Before running on the board, we recommend completing the model performance & accuracy evaluation process described in [**Model Performance Analysis and Tuning**](#performance_evaluation) to avoid extending model conversion issues to the subsequent embedded side.
:::

If any of the three aspects confirming successful model conversion is missing, it indicates an error occurred during model conversion. Generally, the ``makertbin`` tool will output error messages to the console when an error occurs. For example, when converting a Caffe model without configuring the ``prototxt`` and ``caffe_model`` parameters in the YAML file, the model conversion tool gives the following prompt:

```bash
2021-04-21 14:45:34,085 ERROR Key 'model_parameters' error:
Missing keys: 'caffe_model', 'prototxt'
2021-04-21 14:45:34,085 ERROR yaml file parse failed. Please double check your input
2021-04-21 14:45:34,085 ERROR exception in command: makertbin
```
If the console log output does not help you identify the problem, please refer to the [**Model Quantization Errors and Solutions**](../../../08_FAQ/05_toolchain.md#model_convert_errors_and_solutions) section. If the issue persists, contact the D-Robotics technical support team or post your question on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc/). We will provide support within 24 hours.

#### Interpreting Conversion Outputs {#conversion_output}

As mentioned above, the outputs of a successful model conversion include the following four parts. This section describes the purpose of each output:

- \*\*\*_original_float_model.onnx
- \*\*\*_optimized_float_model.onnx
- \*\*\*_calibrated_model.onnx
- \*\*\*_quantized_model.onnx
- \*\*\*.bin

The output process of \*\*\*_original_float_model.onnx can be referenced in [**Interpretation of Internal Conversion Process**](#conversion_interpretation). The computation precision of this model is exactly the same as the input original floating-point model. An important change is the addition of some data preprocessing calculations to adapt to the D-Robotics platform (a preprocessing operator node ``HzPreprocess`` is added; you can use the netron tool to open the ONNX model and view it; details of this operator can be found in the [**Preprocessing HzPreprocess Operator Description**](#pre_process) section). Generally, you do not need to use this model. If an exception occurs in the conversion results and the above-mentioned debugging methods do not resolve the issue, please provide this model to the D-Robotics technical support team or post your question on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc/). This will help you resolve the problem quickly.

The output process of \*\*\*_calibrated_model.onnx can be referenced in [**Interpretation of Internal Conversion Process**](#conversion_interpretation). This model is an intermediate product obtained by the model conversion toolchain after structurally optimizing the floating-point model, calculating the quantization parameters corresponding to each node through the calibration data, and saving them in the calibration nodes.

The output process of \*\*\*_optimized_float_model.onnx can be referenced in [**Interpretation of Internal Conversion Process**](#conversion_interpretation). This model has undergone some operator-level optimization operations, the most common being operator fusion. By comparing visually with the original_float_model, you may notice some changes at the operator structure level, but these do not affect the computational accuracy of the model. Generally, you do not need to use this model. If an exception occurs in the conversion results and the above-mentioned debugging methods do not resolve the issue, please provide this model to the D-Robotics technical support team or post your question on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc/). This will help you resolve the problem quickly.

The output process of \*\*\*_quantized_model.onnx can be referenced in [**Interpretation of Internal Conversion Process**](#conversion_interpretation). This model has completed the calibration and quantization process. The accuracy loss after quantization can be assessed by reading the following content on model accuracy analysis and tuning. This model is essential for the accuracy validation process. For specific usage, please refer to the [**Model Accuracy Analysis and Tuning**](#accuracy_evaluation) section.

\*\*\*.bin is the model that can be loaded and run on a D-Robotics processor. Combined with the content introduced in the "Running on Board (Runtime) Application Development" section, you can quickly deploy the model to run on a D-Robotics processor. However, to ensure that the model's performance and accuracy meet your expectations, it is recommended to complete the performance and accuracy analysis processes described in [**Model Conversion**](#model_conversion) and [**Model Accuracy Analysis and Tuning**](#accuracy_evaluation) before proceeding to application development and deployment.

:::caution Note

  Typically, after completing the model conversion phase, you can obtain a model that runs on a D-Robotics processor. However, to ensure that the performance and accuracy of the model you obtain meet the application requirements, D-Robotics recommends performing the subsequent performance and accuracy evaluation steps after each conversion.

  The ONNX models generated during the model conversion process are intermediate products, intended only to facilitate user validation of model accuracy. Therefore, compatibility between versions is not guaranteed. When using the evaluation scripts in the examples to evaluate a single image or on a test set with an ONNX model, please use the ONNX model regenerated by the current version of the tool.
:::

### Model Performance Analysis {#performance_evaluation}

This section introduces how to use the tools provided by D-Robotics to evaluate model performance. Using these tools, you can obtain performance results that are essentially consistent with actual board execution. If the evaluation results do not meet expectations, it is recommended to resolve performance issues according to the optimization suggestions provided by D-Robotics, rather than extending performance issues to the application development stage.

#### Evaluating Performance on a Development Machine {#hb_perf}

Use the ``hb_perf`` tool to evaluate model performance. The usage is as follows:

```bash
  hb_perf  ***.bin
```
:::info Note
  If analyzing a ``packed`` model, add a ``-p`` parameter, like this: ``hb_perf -p ***.bin``.
  For information about model ``packing``, refer to the "Other Model Tools (Optional)" section.
:::

The \*\*\*.bin in the command is the fixed-point model generated in the model conversion step. After the command execution is complete, a `hb_perf_result` folder is generated in the current directory, containing the specific model analysis results. Below is the evaluation result for the example model MobileNetv1:

```bash
  hb_perf_result/
  └── mobilenetv1_224x224_nv12
      ├── MOBILENET_subgraph_0.html
      ├── MOBILENET_subgraph_0.json
      ├── mobilenetv1_224x224_nv12
      ├── mobilenetv1_224x224_nv12.html
      ├── mobilenetv1_224x224_nv12.png
      └── temp.hbm
```
Open the main page ``mobilenetv1_224x224_nv12.html`` via a browser. Its content looks like the figure below:

![hb_mapper_perf_2](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/hb_mapper_perf_2.png)

The analysis results mainly consist of three parts: Model Performance Summary, Details, and BIN Model Structure.
The Model Performance Summary provides the overall performance evaluation results of the bin model. The metrics are:

- Model Name – The name of the model.
- Model Latency (ms) – The overall single-frame computation time of the model (in ms).
- Total DDR (loaded+stored) bytes per frame (MB per frame) – The total amount of DDR used for loading and storing data by the BPU part of the model (in MB/frame).
- Loaded Bytes per Frame – The amount of data read per frame during model execution.
- Stored Bytes per Frame – The amount of data stored per frame during model execution.

The BIN Model Structure section provides a subgraph-level visualization of the bin model. In the diagram, dark cyan nodes represent nodes running on the BPU, while gray nodes represent nodes computed on the CPU.

When viewing Details and BIN Model Structure, you need to understand the concept of subgraphs. If a CPU operator appears in the model's network structure, the model conversion tool splits the continuous BPU computation parts before and after the CPU operator into two independent subgraphs. For details, refer to the [**Model Verification**](#model_check) section.

Details provides specific information for each BPU subgraph of the model. In the ``mobilenetv1_224x224_nv12.html`` main page, the metrics for each subgraph are:

- Model Subgraph Name – The name of the subgraph.
- Model Subgraph Calculation Load (OPpf) – The single-frame computation amount of the subgraph.
- Model Subgraph DDR Occupation (Mbpf) – The amount of data read and written per frame by the subgraph (in MB).
- Model Subgraph Latency (ms) – The single-frame computation time of the subgraph (in ms).

Each subgraph result provides detailed reference information.

:::caution Note

  The reference information page may differ depending on whether you have enabled debugging configuration. The Layer Details in the figure below is only available when the ``debug`` parameter in the YAML configuration file is set to ``True``. For configuration of this ``debug`` parameter, refer to the [**Using the hb_mapper makertbin tool for model conversion**](#makertbin) section.
:::
Layer Details provides operator-level analysis, which can be used as a reference during model debugging and analysis. For example, if certain BPU operators are causing low model performance, the analysis results can help you locate the specific operators.

![layer_details](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/layer_details.png)

:::caution Note
  The analysis results of the ``hb_perf`` tool help you understand the subgraph structure of the bin model and the static analysis metrics of the BPU computation part within the model. Special attention should be paid that the analysis results do not include the computational evaluation of the CPU part. If you need the performance of CPU computations, please measure the model's performance on the development board.
:::

#### Measuring Performance on a Development Board

To quickly evaluate model performance on the development board, use the ``hrt_model_exec perf`` tool. This tool can directly evaluate the inference performance of the model and obtain model information on the development board.

Before using the ``hrt_model_exec perf`` tool, please prepare:

1. Ensure that you have updated the development board system by referring to the system update section.

2. Copy the bin model obtained on the Ubuntu development machine to the development board (it is recommended to place it in the /userdata directory). The development board runs a Linux system, and this copy process can be completed using common Linux methods like ``scp``.

The ``hrt_model_exec perf`` tool command is as follows (**note that it is executed on the development board**):

```bash
./hrt_model_exec perf --model_file mobilenetv1_224x224_nv12.bin \
                      --model_name="" \
                      --core_id=0 \
                      --frame_count=200 \
                      --perf_time=0 \
                      --thread_num=1 \
                      --profile_path="."
```
Explanation of hrt_model_exec perf parameters:

  model_file:<br/>
    The name of the bin model whose performance is to be analyzed.

  model_name:<br/>
    The name of the bin model. Can be omitted if ``model_file`` contains only one model.

  core_id:<br/>
    Default value ``0``, the core ID used to run the model. ``0`` represents any core, ``1`` represents core 0, ``2`` represents core 1. To analyze the maximum frame rate with dual cores, set this to ``0``.

  frame_count:<br/>
    Default value ``200``, sets the number of inference frames. The tool executes the specified number of times before analyzing the average latency. Effective when ``perf_time`` is ``0``.

  perf_time:<br/>
    Default value ``0``, unit in minutes. Sets the inference time. The tool executes for the specified time before analyzing the average latency.

  thread_num:<br/>
    Default value ``1``, sets the number of running threads. The value range is ``[1,8]``. To analyze the maximum frame rate, increase the number of threads.

  profile_path:<br/>
    Disabled by default. The path where the statistics tool logs are generated. The analysis results introduced by this parameter are stored in the profiler.log and profiler.csv files in the specified directory.

The following example shows the actual measurement results on the **RDK X3** development board. After the command execution is complete, you will get the following log in the console:

```bash
Running condition:
  Thread number is: 1
  Frame count   is: 200
  core number   is: 1
  Program run time: 818.985000 ms
Perf result:
  Frame totally latency is: 800.621155 ms
  Average    latency    is: 4.003106 ms
  Frame      rate       is: 244.204717 FPS
```
:::tip Tip
  In the evaluation results, ``Average latency`` and ``Frame rate`` represent the average single-frame inference latency and the maximum frame rate of the model, respectively. To obtain the maximum frame rate of the model when running on the board, try adjusting the value of ``thread_num`` to find the optimal number of threads, as different values will yield different performance results.
:::

The information obtained from the console only provides an overview. The node_profiler.log file generated by setting the ``profile_path`` parameter contains richer performance information about the model:

```bash
{
  "perf_result": {
    "FPS": 244.20471681410527,
    "average_latency": 4.003105640411377
  },
  "running_condition": {
    "core_id": 0,
    "frame_count": 200,
    "model_name": "mobilenetv1_224x224_nv12",
    "run_time": 818.985,
    "thread_num": 1
  }
}
***
{
  "chip_latency": {
    "BPU_inference_time_cost": {
      "avg_time": 3.42556,
    
  "model_latency": {
    "BPU_MOBILENET_subgraph_0": {
      "avg_time": 3.42556,
      "max_time": 3.823,
      "min_time": 3.057
    },
    "Dequantize_fc7_1_HzDequantize": {
      "avg_time": 0.12307,
      "max_time": 0.274,
      "min_time": 0.044
    },
    "MOBILENET_subgraph_0_output_layout_convert": {
      "avg_time": 0.025945,
      "max_time": 0.069,
      "min_time": 0.012
    },
    "Preprocess": {
      "avg_time": 0.009245,
      "max_time": 0.027,
      "min_time": 0.003
    },
    "Softmax_prob": {
      "avg_time": 0.13366999999999998,
      "max_time": 0.338,
      "min_time": 0.042
    }
  },
  "task_latency": {
    "TaskPendingTime": {
      "avg_time": 0.04952,
      "max_time": 0.12,
      "min_time": 0.009
    },
    "TaskRunningTime": {
      "avg_time": 3.870965,
      "max_time": 4.48,
      "min_time": 3.219
    }
  }
}  "max_time": 3.823,
      "min_time": 3.057
    },
    "CPU_inference_time_cost": {
      "avg_time": 0.29193,
      "max_time": 0.708,
      "min_time": 0.101
    }
  },
  "model_latency": {
    "BPU_MOBILENET_subgraph_0": {
      "avg_time": 3.42556,
      "max_time": 3.823,
      "min_time": 3.057
    },
    "Dequantize_fc7_1_HzDequantize": {
      "avg_time": 0.12307,
      "max_time": 0.274,
      "min_time": 0.044
    },
    "MOBILENET_subgraph_0_output_layout_convert": {
      "avg_time": 0.025945,
      "max_time": 0.069,
      "min_time": 0.012
    },
    "Preprocess": {
      "avg_time": 0.009245,
      "max_time": 0.027,
      "min_time": 0.003
    },
    "Softmax_prob": {
      "avg_time": 0.13366999999999998,
      "max_time": 0.338,
      "min_time": 0.042
    }
  },
  "task_latency": {
    "TaskPendingTime": {
      "avg_time": 0.04952,
      "max_time": 0.12,
      "min_time": 0.009
    },
    "TaskRunningTime": {
      "avg_time": 3.870965,
      "max_time": 4.48,
      "min_time": 3.219
    }
  }
}
```
The above log content corresponds to the bin visualization diagram introduced in the BIN Model Structure section of [**Estimating Performance with the hb_perf tool**](#hb_perf). Each node in the diagram has a corresponding node in the profiler.log file, which can be matched by the ``name``. Additionally, the profiler.log file records the execution time of each node, providing a reference for optimizing model operators. Since BPU nodes in the model have special requirements for input and output, such as specific layout and padding alignment requirements, the input and output data of BPU nodes need to be processed.

- ``Preprocess``: Represents operations such as padding and layout conversion on the model's input data. The time consumption is counted in Preprocess.
- ``xxxx_input_layout_convert``: Represents the padding and layout conversion operations on the input data of a BPU node. The time consumption is counted in xxxx_input_layout_convert.
- ``xxxx_output_layout_convert``: Represents the operation of removing padding and performing layout conversion on the output data of a BPU node. The time consumption is counted in xxxx_output_layout_convert.
``profiler`` analysis is a frequently used operation in model performance tuning. The [**Interpreting Check Results**](#check_result) section mentioned that you don't need to pay too much attention to CPU operators during the checking phase. In this phase, you can see the specific time consumption of CPU operators and can perform model performance tuning based on the time consumption of corresponding operators.

:::tip Tip

  If the model's time consumption is severe, you can also try the following methods for performance optimization:
  1. Single frame, single core: A frame of data comes in, and the model runs inference on one core.
  2. Single frame, dual core: The model is specified as a dual-core model during compilation (core_num: 2 in the YAML configuration file). After running, it automatically occupies the resources of both cores. When a frame of data comes in, it is split into two parts for computation separately, and then the results are combined. This model has a more significant optimization effect on large models, reducing latency to some extent. For small models, it might even slow down due to dual-core scheduling.
  3. Dual frame, dual core: Two cores each run a model independently, processing their respective data frames. Latency does not decrease, but the frame rate can roughly double.
:::

#### Model Performance Optimization

Based on the performance analysis results above, you may find that the model's performance is not as expected. This section introduces D-Robotics' suggestions and measures for improving model performance, including checking YAML configuration parameters, handling CPU operators, recommendations for high-performance model design, and using structures & models friendly to the D-Robotics platform.

:::caution Note
  Some modification suggestions in this section may affect the parameter space of the original floating-point model, thus requiring you to retrain the model. To avoid repeatedly adjusting and training the model during performance tuning, it is recommended to export the model with random parameters to validate performance before achieving satisfactory model performance.
:::

##### Checking YAML Parameters that Affect Model Performance

In the YAML configuration file for model conversion, some parameters actually affect the final performance of the model. Please first check whether they are correctly configured according to your model's expectations. For the specific meaning and function of each parameter, please refer to the [**Compiler Parameters Group**](#compiler_parameters) section.

- ``layer_out_dump``: Specifies whether to output intermediate results of the model during conversion, generally used only for debugging. If set to ``True``, it adds a dequantization output node for each convolution operator, which significantly reduces the model's performance on the board. Therefore, during performance evaluation, be sure to set this parameter to ``False``.
- ``compile_mode``: This parameter is used to choose whether the optimization direction during model compilation is bandwidth or latency. For performance, configure it as ``latency``.
- ``optimize_level``: This parameter is used to choose the compiler's optimization level. In practice, configure it as ``O3`` for the best performance.
- ``core_num``: **Note:** This parameter is only applicable to **RDK X3**. When set to ``2``, it allows both cores to run simultaneously, reducing single-frame inference latency but also affecting overall throughput.
- ``debug``: When set to ``True``, it turns on the compiler's debug mode, which outputs performance simulation-related information, such as frame rate, DDR bandwidth usage, etc. Generally used during the performance evaluation phase. When delivering the product, you can turn off this parameter to reduce model size and improve model execution efficiency.
- ``max_time_per_fc``: This parameter is used to control the execution duration of function calls in the compiled model's data instructions, thereby implementing model priority preemption functionality. Setting this parameter changes the function call execution duration of the preempted model, which will affect the model's performance on the board.

##### Handling CPU Operators

Based on the evaluation of the ``hrt_model_exec perf`` tool, if it is determined that the model's performance bottleneck is caused by CPU operators, it is recommended to check the [**Model Operator Support List**](./supported_op_list) to confirm whether the operators currently running on the CPU have BPU support capability.

If the operator has BPU support capability in the model operator support list, it is likely that the operator's parameters exceed the parameter constraints supported by the BPU. It is recommended to adjust the corresponding original floating-point model's computation parameters to fall within the constraints. To quickly identify the specific parameters that exceed the constraints, it is recommended to perform another check using the method described in the [**Model Verification**](#model_check) section. The tool will directly provide prompts for parameters that exceed the BPU support range.

:::info Note
  The impact of modifying the parameters of the original floating-point model on the model's computational accuracy is your responsibility. For example, Convolution's ``input_channel`` or ``output_channel`` exceeding the range is a typical case. Reducing the channel so that the operator is supported by the BPU, but making only this change may also affect the model's accuracy.
:::

If the operator does not have BPU support capability, you need to take corresponding optimization actions based on the following situations:

- CPU Operator in the Middle of the Model

  For a CPU operator in the middle of the model, it is recommended to prioritize trying parameter adjustments, operator replacement, or modifying the model.

- CPU Operator at the Beginning or End of the Model

  For a CPU operator at the beginning or end of the model, please refer to the following examples, using quantization/dequantization nodes as an example:

  - For nodes connected to the model's input and output, you can add the ``remove_node_type`` parameter in the model_parameters configuration group (model parameters group) of the YAML file and recompile the model.

    ```bash

      remove_node_type: "Quantize; Dequantize"
    ```

    Or use the hb_model_modifier tool to modify the bin model:

    ```bash

      hb_model_modifier x.bin -a Quantize -a Dequantize
    ```

  - For models where the nodes are not connected to the input/output nodes, as shown in the figure below, you need to use the hb_model_modifier tool to determine whether the connected nodes support deletion and then delete them one by one in order.

    ![nodes_connected](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/nodes_connected.png)

    First, use the hb_perf tool to obtain a picture of the model's structure. Then, use the following two commands to remove Quantize nodes from top to bottom. For Dequantize nodes, remove them one by one from bottom to top. The names of nodes that can be deleted at each step can be viewed using ``hb_model_modifier x.bin``.

    ```bash

      hb_model_modifier x.bin -r res2a_branch1_NCHW2NHWC_LayoutConvert_Input0
      hb_model_modifier x_modified.bin -r data_res2a_branch1_HzQuantize
    ```

##### Recommendations for High-Performance Model Design

Based on the performance evaluation results, the time consumption on the CPU may be very small, indicating that the model's performance bottleneck is excessive BPU inference time. When this occurs, it means that the model has already used all of the BPU's computational resources. Therefore, the next step for performance optimization is to improve the utilization of computational resources. Since each processor has its own hardware characteristics, whether the model's computational parameters align well with the corresponding hardware characteristics directly determines the model's computational resource utilization. The higher the alignment, the higher the utilization, and vice versa.

This section focuses on the hardware characteristics of the D-Robotics processor: The D-Robotics processor is designed to accelerate CNNs (Convolutional Neural Networks), with most computational resources dedicated to handling various convolution operations. It is recommended that your model be primarily composed of convolution operations, as operators other than convolution reduce computational resource utilization. The degree of performance impact varies depending on the type of operator.

- **Other Suggestions**

  The computational efficiency of ``depthwise convolution`` on the D-Robotics processor is close to 100%, so for ``MobileNet-like`` models, the BPU has an efficiency advantage.

  It is recommended that during model design, you try to reduce the input and output dimensions of the model's BPU segment to minimize the time spent on quantization, dequantization nodes, and hardware bandwidth pressure. Taking a typical segmentation model as an example, it is recommended to incorporate the Argmax operator directly into the model itself. However, note that Argmax only supports BPU acceleration under the following conditions:

    1. The Softmax layer in Caffe defaults to axis=1, while the ArgMax layer defaults to axis=0. Maintain consistency of the axis when replacing operators.
    2. The channel size of Argmax must be less than or equal to 64; otherwise, it can only be computed on the CPU.

- **BPU Optimizations for High-Efficiency Models**

  The BPU of the D-Robotics processor has made targeted optimizations for both ``Depthwise Convolution`` and ``Group Convolution``. Therefore, we recommend using MobileNetv2, EfficientNet_lite, which adopt Depthwise+Pointwise structures, and D-Robotics' self-developed VarGNet based on GroupConv as the model's backbone for higher performance gains.

  We are continuously exploring more model structures and business models and will provide a richer set of models as direct references for you. These outputs will be updated periodically at https://github.com/D-Robotics/rdk_model_zoo.
  If the above still does not meet your needs, please post on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc) to get in touch with us. We will provide more targeted guidance based on your specific issues.

### Model Accuracy Analysis {#accuracy_evaluation}

The PTQ post-training quantization method, which converts a floating-point model to a fixed-point model using tens or hundreds of calibration images, inevitably introduces some accuracy loss. D-Robotics' PTQ conversion tool, validated by extensive practical use, can typically keep the model's accuracy loss within ``1%`` after selecting the optimal combination of quantization parameters.

This section first introduces how to correctly perform model accuracy analysis. If the evaluation results do not meet expectations, refer to the **Accuracy Tuning** subsection for model accuracy tuning.

#### Accuracy Analysis

As mentioned earlier, the outputs of a successful model conversion include the following four parts:

- \*\*\*_original_float_model.onnx
- \*\*\*_optimized_float_model.onnx
- \*\*\*_quantized_model.onnx
- \*\*\*.bin

Although the final bin model is the one deployed on the D-Robotics processor, to facilitate quickly obtaining model accuracy on the Ubuntu/CentOS development machine, we also support using \*\*\*_quantized_model.onnx to perform model accuracy testing. The \*\*\*_quantized_model.onnx quantized model has the same accuracy effect as the bin model running on the X3 processor.

It is recommended to use the D-Robotics development library to load the ONNX model for inference. The basic process is as follows:

:::caution Note
  1. The example code is not only applicable to the quantized model but also to the original and optimized models. You can prepare data for model inference based on the input type and layout requirements of the different models.

  2. It is recommended to refer to the accuracy validation method for Caffe, ONNX, etc., in the D-Robotics model conversion ``horizon_model_convert_sample`` example package: ``04_inference.sh`` and ``postprocess.py``.
:::

```
# Load the D-Robotics dependency library
from horizon_tc_ui import HB_ONNXRuntime

# Prepare the feed_dict for model execution
def prepare_input_dict(input_names):
  feed_dict = dict()
  for input_name in input_names:
      # your_custom_data_prepare represents your custom data
      # Prepare the data according to the type and layout requirements of the input node
      feed_dict[input_name] = your_custom_data_prepare(input_name)
  return feed_dict

if __name__ == '__main__':
  # Create an inference session
  sess = HB_ONNXRuntime(model_file='***_quantized_model.onnx')

  # Get the input node names
  input_names = [input.name for input in sess.get_inputs()]
  # or
  input_names = sess.input_names

  # Get the output node names
  output_names = [output.name for output in sess.get_outputs()]
  # or
  output_names = sess.output_names

  # Prepare the model input data
  feed_dict = prepare_input_dict(input_names)
  # Start model inference. The return value of inference is a list, corresponding one-to-one with the names specified in output_names.
  # The type range of the input image is (RGB/BGR/NV12/YUV444/GRAY)
  outputs = sess.run(output_names, feed_dict, input_offset=128)
  # The type range of the input data is (FEATURE)
  outputs = sess.run_feature(output_names, feed_dict, input_offset=0)

```

In the above code, the default value of the ``input_offset`` parameter is 128. For models with a preprocessing node, the -128 operation is required here. If the model input does not have a preprocessing node added, set ``input_offset`` to 0.

:::info Note
  For multi-input models:

  - If the input_type_rt of the inputs all belong to (RGB/BGR/NV12/YUV444/GRAY), you can use the sess.run method for inference.

  - If the input_type_rt of the inputs all belong to (FEATUREMAP), you can use the sess.run_feature method for inference.

  - Note that currently, mixed types of FEATUREMAP and non-FEATUREMAP for input_type_rt are not supported for inference using the sess.* methods.
:::
Furthermore, the input data preparation process represented by the ``your_custom_data_prepare`` function is where errors are most likely to occur. Compared to the accuracy validation process of your designed & trained original floating-point model, it is recommended to adjust the inference input data after data preprocessing: mainly regarding data format (RGB, NV12, etc.), data precision (int8, float32, etc.), and data layout (NCHW or NHWC). The adjustment method is determined by the four parameters ``input_type_train``, ``input_layout_train``, ``input_type_rt``, and ``input_layout_rt`` set in the YAML configuration file during model conversion. For detailed rules, refer to the [**Interpretation of Internal Conversion Process**](#conversion_interpretation) section.

For example, consider an original floating-point classification model trained on ImageNet with a single input node. This node accepts three-channel images in BGR order, with an input data layout of NCHW. Then, during the design & training phase of the original floating-point model, the data preprocessing performed before validating the model on the validation set is as follows:

1. Scale the image proportionally, resizing the shorter side to 256.
2. Use the ``center_crop`` method to obtain a 224x224 image.
3. Subtract the mean per channel.
4. Multiply the data by the scale coefficient.

When converting this original floating-point model using D-Robotics, set ``input_type_train`` to ``bgr``, ``input_layout_train`` to ``NCHW``, ``input_type_rt`` to ``bgr``, and ``input_layout_rt`` to ``NHWC``. According to the rules introduced in the [**Interpretation of Internal Conversion Process**](#conversion_interpretation) section, the input accepted by \*\*\*_quantized_model.onnx should be bgr_128, NHWC layout. Corresponding to the earlier example code, the data processing provided by the ``your_custom_data_prepare`` part is as follows:

```
# This example uses skimage; results may differ with OpenCV.
# Note that the transformers do not include mean subtraction or scale multiplication.
# Mean and scale operations have been integrated into the model. Refer to the norm_type/mean_value/scale_value configuration earlier.
def your_custom_data_prepare_sample(image_file):
  # skimage reads the image, already in NHWC layout
  image = skimage.img_as_float(skimage.io.imread(image_file))
  # Scale proportionally, resizing the shorter side to 256
  image = ShortSideResize(image, short_size=256)
  # Obtain 224x224 image using CenterCrop
  image = CenterCrop(image, crop_size=224)
  # skimage reads in RGB channel order; convert to BGR order required by bgr_128
  image = RGB2BGR(image)
  # If the original model is NCHW input (except when input_type_rt is nv12)
  if layout == "NCHW":
    image = HWC2CHW(image)
  # skimage reads values in [0.0,1.0]; adjust to the value range required by bgr
  image = image * 255
  # bgr_128 is bgr minus 128
  image = image - 128
  # bgr_128 uses int8
  image = image.astype(np.int8)
  
  return image
```

#### Accuracy Tuning

Based on the accuracy analysis work above, if it is determined that the model's quantization accuracy does not meet expectations, the situation can be mainly divided into the following two cases for resolution:

- 1. Significant accuracy loss (loss greater than 4%).
  This problem is often caused by improper YAML configuration, imbalanced validation datasets, etc. It is recommended to troubleshoot step by step according to the suggestions provided by D-Robotics below.

- 2. Minor accuracy loss (1.5%~3%).
  After ruling out the issues causing point 1, if there is still a small loss in accuracy, it is often due to the model's own sensitivity. It is recommended to use the accuracy tuning tool provided by D-Robotics for tuning.

- 3. After trying 1 and 2, if the accuracy still cannot meet expectations, you can try using the accuracy debugging tool we provide for further attempts.

The overall accuracy problem-solving process is illustrated below:

![accuracy_problem](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/accuracy_problem.png)

##### Significant Accuracy Loss (Above 4%)

If the model's accuracy loss exceeds 4%, it is usually caused by improper YAML configuration, imbalanced validation datasets, etc. It is recommended to troubleshoot from the following aspects: pipeline, model conversion configuration, and consistency check.

**Pipeline Check**

The pipeline refers to the entire process you follow: data preprocessing, model conversion, model inference, post-processing, and accuracy evaluation. Please check these steps according to the corresponding sections above. Based on past experience in tracking actual problems, we found that in most cases, there were changes during the training phase of the original floating-point model that were not timely updated to the model conversion steps, leading to anomalies during accuracy validation.

**Model Conversion Configuration Check**

- ``input_type_rt`` and ``input_type_train``: These parameters distinguish the data format required by the converted hybrid heterogeneous model from that required by the original floating-point model. Carefully check whether they meet expectations, especially whether the BGR and RGB channel orders are correct.

- Check whether parameters such as ``norm_type``, ``mean_value``, and ``scale_value`` are configured correctly. Mean and scale operation nodes can be directly inserted into the model through the conversion configuration. It is necessary to confirm whether repeated mean and scale operations have been performed on the validation/test images. **Duplicate preprocessing is an error-prone area.**

**Data Processing Consistency Check**

This check is mainly aimed at users who refer to the algorithm toolchain development package examples to prepare calibration data and evaluation code. Common errors include:

- Incorrect specification of ``read_mode``: In 02_preprocess.sh, you can specify the image reading method via the --read_mode parameter, supporting ``opencv`` and ``skimage``. Additionally, in preprocess.py, the imread_mode parameter is also used to set the image reading method and needs to be modified accordingly. Using skimage to read images yields ``RGB`` channel order, a value range of ``0~1``, and a data type of ``float``. Using OpenCV yields ``BGR`` channel order, a value range of ``0~255``, and a data type of ``uint8``.

- Incorrect storage format for the calibration dataset: Currently, D-Robotics uses ``numpy.tofile`` to save calibration data. This method does not save shape and type information. If input_type_train is in a ``non-featuremap`` format, the data type is determined by whether the calibration data storage path contains "f32". If it contains the f32 keyword, the data is parsed as float32; otherwise, it is parsed as uint8. Additionally, to make it easier for users to set the parsing method for calibration data, a new parameter ``cal_data_type`` has been added to the YAML file since X3 algorithm toolchain version v2.2.3a to set the data storage type of the binary file.

- Inconsistent transformer implementation: D-Robotics provides a series of common preprocessing functions, stored in the ``/horizon_model_convert_sample/01_common/python/data/transformer.py`` file. The implementation of some preprocessing operations may differ. For example, ResizeTransformer uses the OpenCV default interpolation method (linear). If another interpolation method is needed, you can directly modify the transformer.py source code to ensure consistency with the preprocessing code during training. For specific usage, refer to the [**transformer usage guide**](../../../08_FAQ/05_toolchain.md#transposetransformer) section.

- It is recommended that during the use of the D-Robotics algorithm toolchain, you still rely on the data processing library used during the training and validation phase of the original floating-point model. For models with poor robustness, typical functions implemented by different libraries, such as resize and crop, can cause disturbances, thereby affecting model accuracy.

- Reasonable setting of the validation image set. The number of calibration images should be around ``one hundred``. It is also best if they can cover various scenarios of the data distribution. For example, in multi-task or multi-classification cases, the validation image set can cover each prediction branch or each category. Also, avoid abnormal images that deviate from the data distribution (e.g., overexposed images).

- Validate the accuracy again using ``***_original_float_model.onnx``. Under normal circumstances, the accuracy of this model should align with the accuracy of the original floating-point model to ``three to five decimal places``. If validation finds that this degree of alignment is not achieved, it indicates that your data processing needs more careful checking.

##### Improving Minor Accuracy Loss

Generally, to reduce the difficulty of model accuracy tuning, it is recommended to first try configuring ``calibration_type`` as ``default``. default is an automatic search function that selects the optimal solution from calibration methods such as max, max-Percentile 0.99995, and KL based on the cosine similarity of the output node of the first calibration image. The finally selected calibration method can be identified by prompts in the conversion log like ``“Select kl method.”``. If the accuracy result from the automatic search still deviates from expectations, try the following suggestions for tuning:

**Adjust the Calibration Method**

- Manually specify calibration_type, choosing ``kl/max``.

- Configure calibration_type as max, and set max_percentile to different percentiles (value range between 0-1). We recommend prioritizing 0.99999, 0.99995, 0.9999, 0.9995, and 0.999. Observe the trend of model accuracy changes through these five configurations to ultimately find an optimal percentile.

- Try enabling ``per_channel``, which can be used in conjunction with any of the previous calibration methods.

**Adjust the Calibration Dataset**

- Try appropriately ``increasing or decreasing`` the amount of data (generally, detection scenarios require less calibration data than classification scenarios; also, observe the model's missed detections and appropriately increase calibration data for corresponding scenarios).

- Do not use abnormal data like pure black or pure white; minimize the use of background images without targets as calibration data. Cover typical task scenarios as comprehensively as possible so that the distribution of the calibration dataset approximates that of the training set.

**Fallback Some Tail Operators to High-Precision CPU Computation**

- Generally, we only try to fallback ``1-2`` operators at the model's output layer to the ``CPU``. Too many operators will significantly affect the model's final performance. The judgment basis can be by observing the model's ``cosine similarity``.

- To specify operators to run on the CPU, use the ``run_on_cpu`` parameter in the YAML file, specifying the node names to run those operators on the CPU (refer to the example: run_on_cpu: conv_0).

- If model compilation fails after setting run_on_cpu, contact the D-Robotics technical support team.

##### Accuracy Debug Tool

After trying the above two accuracy tuning methods, if your accuracy still does not meet expectations, we provide an accuracy debug tool to assist you in locating the problem. This tool helps you perform node-granularity quantization error analysis on the calibration model, quickly identifying nodes that exhibit accuracy anomalies.

:::tip Tip

  If you are using **RDK Ultra and RDK X5** products, you can also try accuracy tuning by configuring some ops to use int16 computation (**RDK X3** does not support int16 computation for operators):

  During model conversion, most ops default to int8 data computation. In some scenarios, using int8 computation for certain ops can lead to significant accuracy loss.
  For **RDK Ultra and RDK X5** products, the algorithm toolchain currently provides the ability to specify particular ops to compute with int16 bits.
  For details, refer to the [**int16 Configuration**](#int16_config) parameter description.
  By configuring quantization-sensitive ops (referenced by cosine similarity) to compute with int16 bits, accuracy loss issues can be resolved in some scenarios.
:::

During model conversion, accuracy loss is inevitably introduced due to the floating-point to fixed-point quantization process. Typically, the main causes of accuracy loss include:

1. Some nodes in the model are sensitive to quantization and introduce large errors, i.e., the sensitive node quantization problem.

2. Error accumulation from various nodes in the model leads to significant calibration errors for the entire model, mainly including error accumulation from weight quantization, activation quantization, and full quantization.

To address this situation, D-Robotics provides an accuracy debug tool to help you independently locate accuracy issues generated during the model quantization process. This tool assists you in performing node-granularity quantization error analysis on the calibration model, ultimately helping you quickly identify nodes with accuracy anomalies.

The accuracy debug tool offers multiple analysis functions for your use, for example:

- Obtain node quantization sensitivity.
- Obtain the model's cumulative error curve.
- Obtain the data distribution of specified nodes.
- Obtain boxplots of inter-channel data distribution for specified node input data, etc.

###### Usage Instructions

Using the accuracy debug tool mainly involves the following steps:

1. Configure the parameter ``debug_mode="dump_calibration_data"`` in the **model parameters group** of the YAML file to save calibration data.

2. Import the debug module and load the calibration model and data.

3. Analyze the model with significant accuracy loss using the API or command line provided by the accuracy debug tool.

:::caution Note

  For the current version of the accuracy debug tool: **RDK Ultra**'s corresponding ``bayes`` architecture models support both command-line and API methods; **RDK X5**'s corresponding ``bayes-e`` architecture models support both command-line and API methods; **RDK X3**'s corresponding ``bernoulli2`` architecture models only support API-based debugging.
:::

The overall process is shown in the figure below:

![accuracy_debug_process](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/accuracy_debug_process.png)

- **Saving the Calibration Model and Data**

First, configure ``debug_mode="dump_calibration_data"`` in the YAML file to enable the accuracy debug function and save the calibration data (calibration_data). The corresponding calibration model (calibrated_model.onnx) is saved as a routine. Here:

1. Calibration data (calibration_data): During the calibration phase, the model performs forward inference on this data to obtain quantization parameters for each quantized node, including scale factors and thresholds.

2. Calibration model (calibrated_model.onnx): The quantization parameters calculated for each quantized node during the calibration phase are saved in the calibration nodes, resulting in the calibration model.

:::caution Note

  **What is the difference between the calibration data saved here and the calibration data generated by 02_preprocess.sh?**

  The calibration data obtained from ``02_preprocess.sh`` is in the BGR color space. Internally, the toolchain converts the data from BGR to the actual input format of the model, such as yuv444/gray.
  The calibration data saved here, however, is in .npy format after color space conversion and preprocessing. This data can be directly loaded using np.load() and fed into the model for inference.
:::

:::caution Note

  **Interpreting the Calibration Model (calibrated_model.onnx)**

  The calibration model is an intermediate product obtained by the model conversion toolchain after structurally optimizing the floating-point model, calculating the quantization parameters corresponding to each node through the calibration data, and saving them in the calibration nodes.
  The main characteristic of the calibration model is that it contains calibration nodes, and the node type of the calibration nodes is HzCalibration.
  These calibration nodes are mainly divided into two categories: **activation calibration nodes** and **weight calibration nodes**.

  The input of an **activation calibration node** is the output of the previous node of the current node. It quantizes and dequantizes the input data based on the quantization parameters (scales and thresholds) saved in the current activation calibration node and then outputs the result.

  The input of a **weight calibration node** is the original floating-point weight of the model. It quantizes and dequantizes the input original floating-point weight based on the quantization parameters (scales and thresholds) saved in the current weight calibration node and then outputs the result.

  Apart from the calibration nodes mentioned above, other nodes in the calibration model are referred to by the accuracy debug tool as **ordinary nodes**. Types of **ordinary nodes** include Conv, Mul, Add, etc.
:::

![debug_node](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/debug_node.png)

The folder structure of calibration_data is as follows:

```shell

  |--calibration_data ：Calibration data
  |----input.1 ：Folder named after the model's input node, storing the corresponding input data
  |--------0.npy
  |--------1.npy
  |-------- ...
  |----input.2 ：For multi-input models, multiple folders will be saved
  |--------0.npy
  |--------1.npy
  |-------- ...
```

- **Importing and Using the Accuracy Debug Module**

Next, you need to import the debug module in your code and use the ``get_sensitivity_of_nodes`` interface to obtain node quantization sensitivity (default uses the cosine similarity of the model's output). For detailed parameter explanations of ``get_sensitivity_of_nodes``, refer to the ``get_sensitivity_of_nodes`` section.

```shell

  # Import the debug module
  import horizon_nn.debug as dbg
  # Import the log module
  import logging

  # If verbose=True, set the log level to INFO first
  logging.getLogger().setLevel(logging.INFO)
  # Get node quantization sensitivity
  node_message = dbg.get_sensitivity_of_nodes(
          model_or_file='./calibrated_model.onnx',
          metrics=['cosine-similarity', 'mse'],
          calibrated_data='./calibration_data/',
          output_node=None,
          node_type='node',
          data_num=None,
          verbose=True,
          interested_nodes=None)
```

- **Display of Analysis Results**

Below are the print results when ``verbose=True``:

```shell

  ==========================node==========================
  Node        cosine-similarity   mse
  --------------------------------------------------------
  Conv_3      0.999009567957658   0.027825591154396534
  MaxPool_2   0.9993462241612948  0.017706592209064044
  Conv_6      0.9998359175828787  0.004541242333988731
  MaxPool_5   0.9998616805443397  0.0038416787014844325
  Conv_0      0.9999297948984     0.0019312848587735342
  Gemm_19     0.9999609772975628  0.0010773885699633795
  Conv_8      0.9999629625907311  0.0010301886404004807
  Gemm_15     0.9999847687207736  0.00041888411550854263
  MaxPool_12  0.9999853235024673  0.0004039733791544747
  Conv_10     0.999985763659844   0.0004040437432614943
  Gemm_17     0.9999913985912616  0.0002379088904350423
```

Additionally, this API returns node quantization sensitivity information in a dictionary format for your subsequent use and analysis.

```shell

  Out: 
  {'Conv_3': {'cosine-similarity': '0.999009567957658', 'mse': '0.027825591154396534'}, 
   'MaxPool_2': {'cosine-similarity': '0.9993462241612948', 'mse': '0.017706592209064044'}, 
   'Conv_6': {'cosine-similarity': '0.9998359175828787', 'mse': '0.004541242333988731'}, 
   'MaxPool_5': {'cosine-similarity': '0.9998616805443397', 'mse': '0.0038416787014844325'}, 
   'Conv_0': {'cosine-similarity': '0.9999297948984', 'mse': '0.0019312848587735342'}, 
   'Gemm_19': {'cosine-similarity': '0.9999609772975628', 'mse': '0.0010773885699633795'}, 
   'Conv_8': {'cosine-similarity': '0.9999629625907311', 'mse': '0.0010301886404004807'}, 
   'Gemm_15': {'cosine-similarity': '0.9999847687207736', 'mse': '0.00041888411550854263'}, 
   'MaxPool_12': {'cosine-similarity': '0.9999853235024673', 'mse': '0.0004039733791544747'}, 
   'Conv_10': {'cosine-similarity': '0.999985763659844', 'mse': '0.0004040437432614943'}, 
   'Gemm_17': {'cosine-similarity': '0.9999913985912616', 'mse': '0.0002379088904350423'}}
```

For more features, refer to the **Function Description** section.

:::tip Tip

  The accuracy debug tool also allows you to view the subcommands for each function via the command line ``hmct-debugger -h/--help``.
  For detailed parameters and usage of each subcommand, refer to the **Function Description** section.
:::

###### Function Description

- **get_sensitivity_of_nodes**

**Function**: Obtains node quantization sensitivity.

**Command Line Format**:

```shell

  hmct-debugger get-sensitivity-of-nodes MODEL_OR_FILE CALIBRATION_DATA --other options
```

You can use ``hmct-debugger get-sensitivity-of-nodes -h/--help`` to view related parameters.

**Parameter Group**:

| Parameter Name | Description | Value Range | Optional/Mandatory |
|------------|----------|----------|--------|
|``model_or_file``| **Function**: Specifies the calibration model.<br/>**Description**: Mandatory, specifies the calibration model to be analyzed.| **Value Range**: None.<br/> **Default**: None.|Mandatory |
|``metrics 或 - m``| **Function**: Metric for node quantization sensitivity.   <br/>**Description**: Specifies the calculation method for node quantization sensitivity. This parameter can be a list, meaning quantization sensitivity is calculated in multiple ways. However, the output results are only sorted by the calculation method listed first. The higher the ranking, the greater the error introduced by quantizing that node.| **Value Range**: ``'cosine-similarity'``, ``'mse'``, ``'mre'``, ``'sqnr'``, ``'chebyshev'``.<br/> **Default**: ``'cosine-similarity'``.|Optional |
|``calibrated_data``| **Function**: Specifies the calibration data.<br/>**Description**: Mandatory, specifies the calibration data required for the analysis.| **Value Range**: None.<br/> **Default**: None.|Mandatory |
|``output_node 或 -o``| **Function**: Specifies the output node.<br/>**Description**: This parameter allows you to specify an intermediate node as the output and calculate node quantization sensitivity based on it. If left as default None, the accuracy debug tool uses the model's final output to calculate node quantization sensitivity.| **Value Range**: Ordinary nodes in the calibration model that have corresponding calibration nodes.<br/> **Default**: None.|Optional |
|``node_type 或 -n``| **Function**: Node type.<br/>**Description**: The type of nodes for which to calculate quantization sensitivity, including: node (ordinary node), weight (weight calibration node), and activation (activation calibration node).| **Value Range**: ``'node'``, ``'weight'``, ``'activation'``.<br/> **Default**: ``'node'``. |Optional |
|``data_num 或 -d``| **Function**: The amount of data needed to calculate quantization sensitivity.<br/>**Description**: Sets the number of data points required for calculating node quantization sensitivity. Defaults to None, meaning all data in calibration_data is used. The minimum setting is 1, and the maximum is the total number of data points in calibration_data.| **Value Range**: Greater than 0, less than or equal to the total number of data points in calibration_data. <br/> **Default**: None|Optional |
|``verbose 或 -v``| **Function**: Selects whether to print information to the terminal.<br/>**Description**: If True, prints quantization sensitivity information to the terminal. If metrics include multiple metrics, sorting is based on the first one.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |
|``interested_nodes 或 -i``| **Function**: Sets nodes of interest.<br/>**Description**: If specified, only obtains the quantization sensitivity for those nodes; other nodes are not obtained. Also, if this parameter is specified, it overrides the node_type specified, meaning this parameter has higher priority than node_type. If left as default None, calculates quantization sensitivity for all quantizable nodes in the model.| **Value Range**: All nodes in the calibration model.<br/> **Default**: None.|Optional |

Function Usage:

```shell

  # Import the debug module
  import horizon_nn.debug as dbg
  # Import the log module
  import logging

  # If verbose=True, set the log level to INFO first
  logging.getLogger().setLevel(logging.INFO)
  # Get node quantization sensitivity
  node_message = dbg.get_sensitivity_of_nodes(
          model_or_file='./calibrated_model.onnx',
          metrics=['cosine-similarity', 'mse'],
          calibrated_data='./calibration_data/',
          output_node=None,
          node_type='node',
          data_num=None,
          verbose=True,
          interested_nodes=None)
```

Command Line Usage:

```shell

  hmct-debugger get-sensitivity-of-nodes calibrated_model.onnx calibration_data -m ['cosine-similarity','mse'] -v True
```

**Analysis Results Display**:

**Description**: First, you set the node type for which to calculate sensitivity via node_type. The tool then obtains all nodes in the calibration model matching node_type and calculates their quantization sensitivity. When verbose is set to True, the tool prints the node quantization sensitivity after sorting to the terminal. The higher the ranking, the greater the quantization error introduced by quantizing that node.

When verbose=True, the print result is as follows:

```shell

  ==========================node==========================
  Node        cosine-similarity   mse
  --------------------------------------------------------
  Conv_3      0.999009567957658   0.027825591154396534
  MaxPool_2   0.9993462241612948  0.017706592209064044
  Conv_6      0.9998359175828787  0.004541242333988731
  MaxPool_5   0.9998616805443397  0.0038416787014844325
  Conv_0      0.9999297948984     0.0019312848587735342
  Gemm_19     0.9999609772975628  0.0010773885699633795
  Conv_8      0.9999629625907311  0.0010301886404004807
  Gemm_15     0.9999847687207736  0.00041888411550854263
  MaxPool_12  0.9999853235024673  0.0004039733791544747
  Conv_10     0.999985763659844   0.0004040437432614943
  Gemm_17     0.9999913985912616  0.0002379088904350423
```

Function Return Value:

  The function returns the quantization sensitivity saved in a dictionary format (Key is the node name, Value is the node's quantization sensitivity information), as shown below:

```shell

  Out: 
  {'Conv_3': {'cosine-similarity': '0.999009567957658', 'mse': '0.027825591154396534'}, 
   'MaxPool_2': {'cosine-similarity': '0.9993462241612948', 'mse': '0.017706592209064044'}, 
   'Conv_6': {'cosine-similarity': '0.9998359175828787', 'mse': '0.004541242333988731'}, 
   'MaxPool_5': {'cosine-similarity': '0.9998616805443397', 'mse': '0.0038416787014844325'}, 
   'Conv_0': {'cosine-similarity': '0.9999297948984', 'mse': '0.0019312848587735342'}, 
   'Gemm_19': {'cosine-similarity': '0.9999609772975628', 'mse': '0.0010773885699633795'}, 
   'Conv_8': {'cosine-similarity': '0.9999629625907311', 'mse': '0.0010301886404004807'}, 
   'Gemm_15': {'cosine-similarity': '0.9999847687207736', 'mse': '0.00041888411550854263'}, 
   'MaxPool_12': {'cosine-similarity': '0.9999853235024673', 'mse': '0.0004039733791544747'}, 
   'Conv_10': {'cosine-similarity': '0.999985763659844', 'mse': '0.0004040437432614943'}, 
   'Gemm_17': {'cosine-similarity': '0.9999913985912616', 'mse': '0.0002379088904350423'}} ...}
```

- **plot_acc_error**

**Function**: Quantizes only one node in the floating-point model at a time, then sequentially calculates the error between the outputs of nodes in this model and the corresponding nodes in the floating-point model, obtaining a cumulative error curve.

**Command Line Format**:

```shell

  hmct-debugger plot-acc-error MODEL_OR_FILE CALIBRATION_DATA --other options
```

You can use ``hmct-debugger plot-acc-error -h/--help`` to view related parameters.

**Parameter Group**:

| Parameter Name | Description | Value Range | Optional/Mandatory |
|------------|----------|----------|--------|
|``save_dir 或 -s``| **Function**: Save path.<br/>**Description**: Optional, specifies the path to save the analysis results. | **Value Range**: None.<br/> **Default**: None.|Optional |
|``calibrated_data``| **Function**: Specifies the calibration data. <br/>**Description**: Mandatory, specifies the calibration data to be analyzed.| **Value Range**: None.<br/> **Default**: None.|Mandatory |
|``model_or_file``| **Function**: Specifies the calibration model.<br/>**Description**: Mandatory, specifies the calibration model to be analyzed. | **Value Range**: None.<br/> **Default**: None.|Mandatory |
|``quantize_node 或 -q``| **Function**: Quantizes only the specified nodes in the model to view the error accumulation curve.<br/>**Description**: Optional parameter. Specifies the nodes in the model that need to be quantized, while ensuring that the remaining nodes are not quantized.<br/>Determines whether it is single-node quantization or partial quantization by checking if this parameter is a nested list.<br/>For example:<br/>- quantize_node=['Conv_2','Conv_9']: Quantizes only Conv_2 and Conv_9 separately, while ensuring other nodes are not quantized.<br/>- quantize_node=[['Conv_2'],['Conv_9','Conv_2']]: Quantizes only Conv_2 and simultaneously quantizes Conv_2 and Conv_9, testing the model's cumulative error for each case.<br/>- quantize_node includes two special parameters: 'weight' and 'activation'.<br/>When:<br/>- quantize_node = ['weight']: Quantizes only weights, not activations.<br/>- quantize_node = ['activation']: Quantizes only activations, not weights.<br/>- quantize_node = ['weight','activation']: Quantizes weights and activations separately.<br/>Note: quantize_node and non_quantize_node cannot both be None; one must be specified.| **Value Range**: All nodes in the calibration model.<br/> **Default**: None.|Optional |
|``non_quantize_node 或 -nq``| **Function**: Specifies the type of cumulative error.<br/>**Description**: Optional parameter. Specifies the nodes in the model that are not quantized, while ensuring that the remaining nodes are all quantized.<br/>Determines whether it is single-node non-quantization or partial non-quantization by checking if this parameter is a nested list.<br/>For example:<br/>- non_quantize_node=['Conv_2','Conv_9']: De-quantizes Conv_2 and Conv_9 separately, while ensuring other nodes are quantized.<br/>- non_quantize_node=[['Conv_2'],['Conv_9','Conv_2']]: De-quantizes only Conv_2 and simultaneously de-quantizes Conv_2 and Conv_9, testing the model's cumulative error for each case. <br/>Note: quantize_node and non_quantize_node cannot both be None; one must be specified.| **Value Range**: All nodes in the calibration model.<br/> **Default**: None.|Optional |
|``metric 或 -m``| **Function**: Error metric.<br/>**Description**: Sets the calculation method for model error.| **Value Range**: ``'cosine-similarity'``, ``'mse'``, ``'mre'``, ``'sqnr'``, ``'chebyshev'``<br/> **Default**: ``'cosine-similarity'``.|Optional |
|``average_mode 或 -a``| **Function**: Specifies the output mode for the cumulative error curve.<br/>**Description**: Defaults to False. If True, the average of the cumulative errors is used as the result.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |

```shell

  # Import the debug module
  import horizon_nn.debug as dbg

  dbg.plot_acc_error(
          save_dir: str,
          calibrated_data: str or CalibrationDataSet,
          model_or_file: ModelProto or str,
          quantize_node: List or str,
          non_quantize_node: List or str,
          metric: str = 'cosine-similarity',
          average_mode: bool = False)
```

**Analysis Results Display**

**1. Specified Node Quantization Cumulative Error Test**

- Specifying single node quantization

**Configuration**: quantize_node=['Conv_2', 'Conv_90'], where quantize_node is a single list.

API Function Usage:

```shell

  # Import the debug module
  import horizon_nn.debug as dbg

  dbg.plot_acc_error(
          save_dir='./',
          calibrated_data='./calibration_data/',
          model_or_file='./calibrated_model.onnx',
          quantize_node=['Conv_2', 'Conv_90'],
          metric='cosine-similarity',
          average_mode=False)
```

Command Line Usage:

```shell

  hmct-debugger plot-acc-error calibrated_model.onnx calibrated_data -q ['Conv_2','Conv_90']
```

**Description**: When quantize_node is a single list, for the quantize_node you set, it separately quantizes each node in quantize_node while keeping other nodes in the model unquantized. After obtaining the corresponding model, it calculates the error between the output of each node in this model and the output of the corresponding node in the floating-point model, and then obtains the corresponding cumulative error curve.

When average_mode = False:

![average_mode_false_1](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/average_mode_false_1.png)

When average_mode = True:

![average_mode_true_1](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/average_mode_true_1.png)

:::caution Note

  **average_mode**

  average_mode defaults to False. For some models, it may be impossible to determine which quantization strategy is more effective from the cumulative error curve at this point. Therefore, you need to set average_mode to True, which averages the cumulative errors of the first n nodes as the cumulative error of the nth node.

  The specific calculation method is as follows, for example:

  When average_mode=False, accumulate_error=[1.0, 0.9, 0.9, 0.8].

  After setting average_mode=True, accumulate_error=[1.0, 0.95, 0.933, 0.9].
:::

- Specifying quantization of multiple nodes

**Configuration**: quantize_node=[['Conv_2'], ['Conv_2', 'Conv_90']], where quantize_node is a nested list.

API Usage:

```shell

  # Import the debug module
  import horizon_nn.debug as dbg

  dbg.plot_acc_error(
          save_dir='./',
          calibrated_data='./calibration_data/',
          model_or_file='./calibrated_model.onnx',
          quantize_node=[['Conv_2'], ['Conv_2', 'Conv_90']],
          metric='cosine-similarity',
          average_mode=False)
```

Command Line Usage:

```shell

  hmct-debugger plot-acc-error calibrated_model.onnx calibration_data -q [['Conv_2'],['Conv_2','Conv_90']]
```

**Description**: When quantize_node is a nested list, for the quantize_node you set, it quantizes the nodes specified by each single list within quantize_node while keeping other nodes in the model unquantified. After obtaining the corresponding model, it calculates the error between the output of each node in this model and the output of the corresponding node in the floating-point model, and then obtains the corresponding cumulative error curve.

- partial_qmodel_0: Only quantizes the Conv_2 node, other nodes are not quantized.

- partial_qmodel_1: Only quantizes Conv_2 and Conv_90 nodes, other nodes are not quantized.

When average_mode = False:

![new_average_mode_false_1](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/new_average_mode_false_1.png)

When average_mode = True:

![new_average_mode_true_1](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/new_average_mode_true_1.png)

**2. Cumulative Error Test after De-quantizing Some Nodes of the Model**

- Specifying single node de-quantization

**Configuration**: non_quantize_node=['Conv_2', 'Conv_90'], where non_quantize_node is a single list.

API Usage:

```shell

  # Import the debug module
  import horizon_nn.debug as dbg

  dbg.plot_acc_error(
          save_dir='./',
          calibrated_data='./calibration_data/',
          model_or_file='./calibrated_model.onnx',
          non_quantize_node=['Conv_2', 'Conv_90'],
          metric='cosine-similarity',
          average_mode=True)
```

Command Line Usage:

```shell

  hmct-debugger plot-acc-error calibrated_model.onnx calibration_data -nq ['Conv_2','Conv_90'] -a True
```

**Description**: When non_quantize_node is a single list, for the non_quantize_node you set, it separately de-quantizes each node in non_quantize_node while keeping other nodes quantized. After obtaining the corresponding model, it calculates the error between the output of each node in this model and the output of the corresponding node in the floating-point model, and then obtains the corresponding cumulative error curve.

When average_mode = False:

![average_mode_false_2](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/average_mode_false_2.png)

When average_mode = True:

![average_mode_true_2](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/average_mode_true_2.png)

- Specifying de-quantization of multiple nodes

**Configuration**: non_quantize_node=[['Conv_2'], ['Conv_2', 'Conv_90']], where non_quantize_node is a nested list.

API Usage:

```shell

  # Import the debug module
  import horizon_nn.debug as dbg

  dbg.plot_acc_error(
          save_dir='./',
          calibrated_data='./calibration_data/',
          model_or_file='./calibrated_model.onnx',
          non_quantize_node=[['Conv_2'], ['Conv_2', 'Conv_90']],
          metric='cosine-similarity',
          average_mode=False)
```

Command Line Usage:

```shell

  hmct-debugger plot-acc-error calibrated_model.onnx calibration_data -nq [['Conv_2'],['Conv_2','Conv_90']]
```

**Description**: When non_quantize_node is a nested list, for the non_quantize_node you set, it de-quantizes the nodes specified by each single list within non_quantize_node while keeping other nodes in the model quantized. After obtaining the corresponding model, it calculates the error between the output of each node in this model and the output of the corresponding node in the floating-point model, and then obtains the corresponding cumulative error curve.

- partial_qmodel_0: De-quantizes the Conv_2 node, other nodes are quantized.

- partial_qmodel_1: De-quantizes Conv_2 and Conv_90 nodes, other nodes are quantized.

When average_mode = False:

![new_average_mode_false_2](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/new_average_mode_false_2.png)

When average_mode = True:

![new_average_mode_true_2](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/new_average_mode_true_2.png)

**Testing Tip**:

When testing the accuracy of partial quantization, you may want to compare the accuracy of multiple quantization strategies based on the quantization sensitivity ranking. In this case, you can refer to the following usage:

```shell

  # Import the debug module
  import horizon_nn.debug as dbg

  # First, use the quantization sensitivity sorting function to get the quantization sensitivity ranking of nodes in the model
  node_message = dbg.get_sensitivity_of_nodes(
          model_or_file='./calibrated_model.onnx',
          metrics='cosine-similarity',
          calibrated_data='./calibration_data/',
          output_node=None,
          node_type='node',
          verbose=False,
          interested_nodes=None)
        
  # node_message is a dictionary type, its keys are node names
  nodes = list(node_message.keys())

  # Specify non-quantized nodes through nodes for easy use
  dbg.plot_acc_error(
          save_dir='./',
          calibrated_data='./calibration_data/',
          model_or_file='./calibrated_model.onnx',
          non_quantize_node=[nodes[:1],nodes[:2]],
          metric='cosine-similarity',
          average_mode=True)
```

**3. Separate Quantization of Weights and Activations**

**Configuration**: quantize_node=['weight','activation'].

API Usage:

```shell

  import horizon_nn.debug as dbg

  dbg.plot_acc_error(
          save_dir='./',
          calibrated_data='./calibration_data/',
          model_or_file='./calibrated_model.onnx',
          quantize_node=['weight','activation'],
          metric='cosine-similarity',
          average_mode=False)
```

Command Line Usage:

```shell

  hmct-debugger plot_acc_error calibrated_model.onnx calibration_data -q ['weight','activation']
```

**Description**: quantize_node can also directly specify 'weight' or 'activation'. When:

- quantize_node = ['weight']: Quantizes only weights, not activations.

- quantize_node = ['activation']: Quantizes only activations, not weights.

- quantize_node = ['weight', 'activation']: Quantizes weights and activations separately.

![weight_activation_quantized](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/weight_activation_quantized.png)

- **plot_distribution**

**Function**: Selects a node, obtains the output of that node in both the floating-point model and the calibration model, and displays the distribution of the output data. Additionally, it subtracts the two output results to obtain the error distribution between the two outputs.

**Command Line Format**:

```shell

  hmct-debugger plot-distribution MODEL_OR_FILE CALIBRATION_DATA --other options
```

You can use ``hmct-debugger plot-distribution -h/--help`` to view related parameters.

**Parameter Group**:

| Parameter Name | Description | Value Range | Optional/Mandatory |
|------------|----------|----------|--------|
|``save_dir 或 -s``| **Function**: Save path.<br/>**Description**: Optional, specifies the path to save the analysis results.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``model_or_file``| **Function**: Specifies the calibration model.<br/>**Description**: Mandatory, specifies the calibration model to be analyzed.| **Value Range**: None.<br/> **Default**: None.|Mandatory |
|``calibrated_data``| **Function**: Specifies the calibration data.<br/>**Description**: Mandatory, specifies the calibration data required for the analysis.| **Value Range**: None.<br/> **Default**: None.|Mandatory |
|``nodes_list 或 -n``| **Function**: Specifies the nodes to be analyzed.<br/>**Description**: Mandatory, specifies the nodes to be analyzed.<br/>If the node type in nodes_list is:<br/>- Weight calibration node: Plots the data distribution of the original weights and the weights after calibration.<br/>- Activation calibration node: Plots the input data distribution of the activation calibration node.<br/>- Ordinary node: Plots the output data distribution of the node before and after quantization, and also plots the error distribution between the two.<br/>Note: nodes_list is of type list; you can specify a series of nodes, and the three types of nodes mentioned above can be specified simultaneously.| **Value Range**: All nodes in the calibration model.<br/> **Default**: None.|Mandatory |

```shell

  # Import the debug module
  import horizon_nn.debug as dbg

  dbg.plot_distribution(
          save_dir: str, 
          model_or_file: ModelProto or str,
          calibrated_data: str or CalibrationDataSet,
          nodes_list: List[str] or str) 
```

**Analysis Results Display**:

API Usage:

```shell

  # Import the debug module
  import horizon_nn.debug as dbg

  dbg.plot_distribution(
          save_dir='./',
          model_or_file='./calibrated_model.onnx',
          calibrated_data='./calibration_data',
          nodes_list=['317_HzCalibration', # Activation node
                      '471_HzCalibration', # Weight node
                      'Conv_2']) # Ordinary node
```

Command Line Usage:

```shell

  hmct-debugger plot-distribution calibrated_model.onnx calibration_data -n ['317_HzCalibration','471_HzCalibration','Conv_2']
```

node_output:

![node_output](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/node_output.png)

weight:

![weight](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/weight.png)

activation:

![activation](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/activation.png)

:::caution Note

  In the three figures above, the blue triangle indicates: the maximum absolute value of the data. The red dashed line indicates: the minimum calibration threshold.
:::

- **get_channelwise_data_distribution**

**Function**: Draws boxplots of the data distribution across channels of the input data of a specified calibration node.

**Command Line Format**:

```shell

  hmct-debugger get-channelwise-data-distribution MODEL_OR_FILE CALIBRATION_DATA --other options
```

You can use ``hmct-debugger get-channelwise-data-distribution -h/--help`` to view related parameters.

**Parameter Group**:

| Parameter Name | Description | Value Range | Optional/Mandatory |
|------------|----------|----------|--------|
|``save_dir 或 -s``| **Function**: Save path.<br/>**Description**: Optional, specifies the path to save the analysis results.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``model_or_file``| **Function**: Specifies the calibration model. <br/>**Description**: Mandatory, specifies the calibration model to be analyzed.| **Value Range**: None.<br/> **Default**: None.|Mandatory |
|``calibrated_data``| **Function**: Specifies the calibration data.<br/>**Description**: Mandatory, specifies the calibration data required for the analysis. | **Value Range**: None.<br/> **Default**: None.|Mandatory |
|``nodes_list 或 -n``| **Function**: Specifies the calibration nodes.<br/>**Description**: Mandatory, specifies the calibration nodes.| **Value Range**: All weight calibration nodes and activation calibration nodes in the calibration model.<br/> **Default**: None.|Mandatory |
|``axis 或 -a``| **Function**: Specifies the dimension where the channel is located.<br/>**Description**: The position of the channel information within the shape. The parameter defaults to None. In this case, for activation calibration nodes, the second dimension of the node's input data is assumed to represent channel information, i.e., axis=1; for weight calibration nodes, the axis parameter in the node's attributes is read as the channel information. | **Value Range**: Less than the dimension of the node's input data. <br/> **Default**: None.|Optional |

```shell

  # Import the debug module
  import horizon_nn.debug as dbg

  dbg.get_channelwise_data_distribution(
          save_dir: str, 
          model_or_file: ModelProto or str,
          calibrated_data: str or CalibrationDataSet,
          nodes_list: List[str],
          axis: int = None)
```

**Analysis Results Display**:

**Description**: For the user-specified list of calibration nodes node_list, the axis parameter is used to obtain the dimension where the channel is located, and the data distribution across channels of the node's input data is obtained. axis defaults to None. In this case, if the node is a weight calibration node, the dimension where the channel is located defaults to 0; if the node is an activation calibration node, the dimension where the channel is located defaults to 1.

Weight calibration node:

![weight_calibration_node](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/weight_calibration_node.png)

Activation calibration node:

![activate_calibration_node](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/activate_calibration_node.png)

The output result is shown in the figure below:

![box_plot](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/box_plot.png)

In the figure:

  - The horizontal axis represents the number of channels of the node's input data. In the legend, the input data has 96 channels.

  - The vertical axis represents the data distribution range for each channel. The solid red line indicates the median of the data for that channel, and the blue dashed line indicates the mean.

- **runall**

:::caution Note

  The runall function in the current version is only applicable to **RDK Ultra and RDK X5** products.
:::

**Function**: Runs all functions in the original debug tool with a single command.

**Command Line Format**:

```shell

  hmct-debugger runall MODEL_OR_FILE CALIBRATION_DATA --other options
```

You can use ``hmct-debugger runall -h/--help`` to view related parameters.
 
**Parameter Group**:

| Parameter Name | Description | Value Range | Optional/Mandatory |
|------------|----------|----------|--------|
|``model_or_file``| **Function**: Specifies the calibration model.<br/>**Description**: Mandatory, specifies the calibration model to be analyzed.| **Value Range**: None.<br/> **Default**: None.|Mandatory |
|``calibrated_data``| **Function**: Specifies the calibration data.<br/>**Description**: Mandatory, specifies the calibration data required for the analysis.| **Value Range**: None.<br/> **Default**: None.|Mandatory |
|``save_dir 或 -s``| **Function**: Save path.<br/>**Description**: Specifies the path to save the analysis results.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``ns_metrics 或 -nm``| **Function**: Metric for node quantization sensitivity.<br/>**Description**: Specifies the calculation method for node quantization sensitivity. This parameter can be a list, meaning quantization sensitivity is calculated in multiple ways. However, the output results are only sorted by the calculation method listed first. The higher the ranking, the greater the error introduced by quantizing that node.| **Value Range**: ``'cosine-similarity'``, ``'mse'``, ``'mre'``, ``'sqnr'``, ``'chebyshev'``.<br/> **Default**: ``'cosine-similarity'``.|Optional |
|``output_node 或 -o``| **Function**: Specifies the output node.<br/>**Description**: This parameter allows you to specify an intermediate node as the output and calculate node quantization sensitivity based on it. If left as default None, the accuracy debug tool uses the model's final output to calculate node quantization sensitivity.| **Value Range**: Ordinary nodes in the calibration model that have corresponding calibration nodes.<br/> **Default**: None.|Optional |
|``node_type 或 -nt``| **Function**: Node type.<br/>**Description**: The type of nodes for which to calculate quantization sensitivity, including: node (ordinary node), weight (weight calibration node), and activation (activation calibration node).| **Value Range**: ``'node'``, ``'weight'``, ``'activation'``.<br/> **Default**: ``'node'``.|Optional |
|``data_num 或 -dn``| **Function**: The amount of data needed to calculate quantization sensitivity.<br/>**Description**: Sets the number of data points required for calculating node quantization sensitivity. Defaults to None, meaning all data in calibration_data is used. The minimum setting is 1, and the maximum is the total number of data points in calibration_data.| **Value Range**: Greater than 0, less than or equal to the total number of data points in calibration_data.<br/> **Default**: None .|Optional |
|``verbose 或 -v``| **Function**: Selects whether to print information to the terminal.<br/>**Description**: If True, prints quantization sensitivity information to the terminal. If metrics include multiple metrics, sorting is based on the first one.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |
|``interested_nodes 或 -i``| **Function**: Sets nodes of interest.<br/>**Description**: If specified, only obtains the quantization sensitivity for those nodes; other nodes are not obtained. Also, if this parameter is specified, it overrides the node_type specified, meaning this parameter has higher priority than node_type. If left as default None, calculates quantization sensitivity for all quantizable nodes in the model.| **Value Range**: All nodes in the calibration model.<br/> **Default**: None.|Optional |
|``dis_nodes_list 或 -dnl``| **Function**: Specifies the nodes to be analyzed.<br/>**Description**: Specifies the nodes to be analyzed.<br/>If the node type in nodes_list is:<br/>- Weight calibration node: Plots the data distribution of the original weights and the weights after calibration.<br/>- Activation calibration node: Plots the input data distribution of the activation calibration node.<br/>- Ordinary node: Plots the output data distribution of the node before and after quantization, and also plots the error distribution between the two.<br/>Note: nodes_list is of type list; you can specify a series of nodes, and the three types of nodes mentioned above can be specified simultaneously.| **Value Range**: All nodes in the calibration model.<br/> **Default**: None.|Optional |
|``cw_nodes_list 或 -cn``| **Function**: Specifies the calibration nodes.<br/>**Description**: Specifies the calibration nodes.| **Value Range**: All weight calibration nodes and activation calibration nodes in the calibration model.<br/> **Default**: None.|Optional |
|``axis 或 -a``| **Function**: Specifies the dimension where the channel is located. <br/>**Description**: The position of the channel information within the shape. The parameter defaults to None. In this case, for activation calibration nodes, the second dimension of the node's input data is assumed to represent channel information, i.e., axis=1; for weight calibration nodes, the axis parameter in the node's attributes is read as the channel information.| **Value Range**: Less than the dimension of the node's input data.<br/> **Default**: None.|Optional |
|``quantize_node 或 -qn``| **Function**: Quantizes only the specified nodes in the model to view the error accumulation curve.<br/>**Description**: Optional parameter. Specifies the nodes in the model that need to be quantized, while ensuring that the remaining nodes are not quantized.<br/>Determines whether it is single-node quantization or partial quantization by checking if this parameter is a nested list.<br/>For example:<br/>- quantize_node=['Conv_2','Conv_9']: Quantizes only Conv_2 and Conv_9 separately, while ensuring other nodes are not quantized.<br/>- quantize_node=[['Conv_2'],['Conv_9','Conv_2']]: Quantizes only Conv_2 and simultaneously quantizes Conv_2 and Conv_9, testing the model's cumulative error for each case.<br/>- quantize_node includes two special parameters: 'weight' and 'activation'.<br/>When:<br/>- quantize_node = ['weight']: Quantizes only weights, not activations.<br/>- quantize_node = ['activation']: Quantizes only activations, not weights.<br/>- quantize_node = ['weight','activation']: Quantizes weights and activations separately.<br/>Note: quantize_node and non_quantize_node cannot both be None; one must be specified.| **Value Range**: All nodes in the calibration model.<br/> **Default**: None.|Optional |
|``non_quantize_node 或 -nqn``| **Function**: Specifies the type of cumulative error.<br/>**Description**: Optional parameter. Specifies the nodes in the model that are not quantized, while ensuring that the remaining nodes are all quantized.<br/>Determines whether it is single-node non-quantization or partial non-quantization by checking if this parameter is a nested list.<br/>For example:<br/>- non_quantize_node=['Conv_2','Conv_9']: De-quantizes Conv_2 and Conv_9 separately, while ensuring other nodes are quantized.<br/>- non_quantize_node=[['Conv_2'],['Conv_9','Conv_2']]: De-quantizes only Conv_2 and simultaneously de-quantizes Conv_2 and Conv_9, testing the model's cumulative error for each case. <br/>Note: quantize_node and non_quantize_node cannot both be None; one must be specified.| **Value Range**: All nodes in the calibration model.<br/> **Default**: None.|Optional |
|``ae_metric 或 -am``| **Function**: Cumulative error metric.<br/>**Description**: Sets the calculation method for model error.| **Value Range**: ``'cosine-similarity'``, ``'mse'``, ``'mre'``, ``'sqnr'``, ``'chebyshev'`` <br/> **Default**: ``'cosine-similarity'``.|Optional |
|``average_mode 或 -avm``| **Function**: Specifies the output mode for the cumulative error curve.<br/>**Description**: Defaults to False. If True, the average of the cumulative errors is used as the result.| **Value Range**: ``True``, ``False``.<br/> **Default**: ``False``.|Optional |

API Usage:

```shell

  # Import the debug module
  import horizon_nn.debug as dbg
  
  dbg.runall(model_or_file='calibrated_model.onnx',
             calibrated_data='calibration_data')
```

Command Line Usage:

```shell

  hmct-debugger runall calibrated_model.onnx calibration_data
```

runall Process:

![runall](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/runall.png)

When all parameters are left at their defaults, the tool will execute the following functions sequentially:

1. Obtain the quantization sensitivity of weight calibration nodes and activation calibration nodes separately.

2. Based on the results from step 1, take the top 5 weight calibration nodes and the top 5 activation calibration nodes and plot their data distribution.

3. For the nodes obtained in step 2, plot boxplots of the inter-channel data distribution.

4. Plot the cumulative error curves for quantizing only weights and only activations, respectively.

When ``node_type='node'`` is specified, the tool obtains the top 5 nodes, finds the corresponding calibration node for each, and obtains the data distribution and boxplot of the calibration nodes.

Based on past usage and tuning experience, the above strategies can handle various practical problems.

If, after trying the above, you still haven't been able to resolve your issue, please check the specific information of your model configuration according to the steps in the [**Accuracy Tuning Checklist**](../../../08_FAQ/05_toolchain.md#checklist) document. Ensure that each step of the troubleshooting has been completed, and lock down the specific step in the model conversion where the anomaly occurred. Then, provide the completed **Accuracy Tuning Checklist** information, the original floating-point model file, and the configuration files related to model quantization to the D-Robotics technical support team or post your question on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc/). We will provide support within 24 hours.

### Other Tool Usage Instructions

This chapter mainly introduces the usage of other debug tools besides the model conversion tool. These tools can assist developers in operations such as model modification, model analysis, and data preprocessing. The tools list is as follows:

- hb_perf

- hb_pack

- hb_model_info

- hb_model_modifier

- hb_model_verifier

- hb_eval_preprocess

#### The ``hb_perf`` Tool

``hb_perf`` is an analysis tool for analyzing the performance of D-Robotics quantized hybrid models.

- Usage

```
hb_perf [OPTIONS] BIN_FILE
```
- Command Line Parameters

Command line parameters for hb_perf:

  --version<br/>
    Displays the version and exits.

  -m<br/>
    Followed by the model name. When the specified BIN_FILE is a packed model, only outputs the compilation information of the specified model.
    
  --help<br/>
    Displays help information.

- Output Description

The model information is output in the `hb_perf_result` folder in the current directory. Inside, there will be a folder named after the model, and the model information will be displayed in an `html` file named after the model name. The directory structure is shown in the following example:

```shell
  hb_perf_result/
  └── mobilenetv1
      ├── mobilenetv1
      ├── mobilenetv1.html
      ├── mobilenetv1.png
      ├── MOBILENET_subgraph_0.html
      ├── MOBILENET_subgraph_0.json
      └── temp.hbm
```

If the model was not compiled with debug mode enabled (``compiler_parameters.debug:True``), the ``hb_perf`` tool will produce the following prompt. This prompt only indicates that the subgraph information does not include per-layer information and does not affect the generation of overall model information.
```
2021-01-12 10:41:40,000 WARNING bpu model don't have per-layer perf info.
2021-01-12 10:41:40,000 WARNING if you need per-layer perf info please enable[compiler_parameters.debug:True] when use makertbin.
```

#### The ``hb_pack`` Tool

``hb_pack`` is a tool for packaging multiple hybrid model (\*.bin) files into a single model file.

- Usage

```
hb_pack [OPTIONS] BIN_FILE1 BIN_FILE2 BIN_FILE3 -o comb.bin
```

- Command Line Parameters

Command line parameters for hb_pack:

  --version<br/>
    Displays the version and exits.

  -o, --output_name<br/>
    The output name for the packed model.

  --help<br/>
    Displays help information.

- Output Description

The packed model is output in a folder in the current directory and is named according to the name specified by ``output_name``. The compilation information and performance information of all submodels within this packed model can be obtained via ``hb_model_info`` and ``hb_perf``.

:::caution Note
  Note that ``hb_pack`` does not support repacking an already packed model. Otherwise, the console will produce the following prompt:
:::
```bash
ERROR exception in command: pack
ERROR model: xxx.bin is a packed model, it can not be packed again!
```

#### The ``hb_model_info`` Tool

``hb_model_info`` is a tool for parsing the dependencies and parameter information during the compilation of a hybrid model (\*.bin).

- Usage

```bash
  hb_model_info ${model_file}
```
- Command Line Parameters

Command line parameters for hb_model_info:

  --version<br/>
    Displays the version and exits.

  -m<br/>
    Followed by the model name. When the specified BIN_FILE is a packed model, only outputs the compilation information of the specified model.

  --help<br/>
    Displays help information.

- Output Description

The output will be some input information during model compilation, as shown below:

:::info Note
  The version numbers in the code block below will vary with the release package version; this is just an example.
:::
```bash
Start hb_model_info....
hb_model_info version 1.3.35
******** efficient_det_512x512_nv12 info *********
############# model deps info #############
hb_mapper version   : 1.3.35
hbdk version        : 3.23.3
hbdk runtime version: 3.13.7
horizon_nn version  : 0.10.10
############# model_parameters info #############
onnx_model          : /release/01_common/model_zoo/mapper/detection/efficient_det/efficientdet_nhwc.onnx
BPU march           : bernoulli2
layer_out_dump      : False
working dir         : /release/04_detection/05_efficient_det/mapper/model_output
output_model_file_prefix: efficient_det_512x512_nv12
############# input_parameters info #############
------
---------input info : data ---------
input_name          : data
input_type_rt       : nv12
input_space&range   : regular
input_layout_rt     : None
input_type_train    : rgb
input_layout_train  : NCHW
norm_type           : data_mean_and_scale
input_shape         : 1x3x512x512
mean_value          : 123.68,116.779,103.939,
scale_value         : 0.017,
cal_data_dir        : /release/04_detection/05_efficient_det/mapper/calibration_data_rgb_f32
---------input info : data end -------
------
############# calibration_parameters info #############
preprocess_on       : False
calibration_type    : max
############# compiler_parameters info #############
hbdk_pass_through_params: --fast --O3
input-source        : {'data': 'pyramid', '_default_value': 'ddr'}
--------- input/output types -
model input types   : [<InputDataType.NV12: 7>]
model output types  : [<InputDataType.F32: 5>, <InputDataType.F32: 5>, <InputDataType.F32: 5>, <InputDataTye.F32: 5>, <InputDataType.F32: 5>, <InputDataType.F32: 5>, <InputDataType.F32: 5>, <InputDataType.F32: 5>, <InputDataType.F32: 5>, <InpuDataType.F32: 5>]
```
:::info Note

  When there are deleted nodes in the model, the names of the deleted nodes will be printed at the end of the model information output, and a ``deleted_nodes_info.txt`` file will be generated. Each line in the file records the initial information of the corresponding deleted node. The printout of the deleted node names is shown below:
:::

```bash
--------- deleted nodes -
deleted nodes: spconvretinanethead0_conv91_fwd_chw_HzDequantize
deleted nodes: spconvretinanethead0_conv95_fwd_chw_HzDequantize
deleted nodes: spconvretinanethead0_conv99_fwd_chw_HzDequantize
deleted nodes: spconvretinanethead0_conv103_fwd_chw_HzDequantize
deleted nodes: spconvretinanethead0_conv107_fwd_chw_HzDequantize
deleted nodes: spconvretinanethead0_conv93_fwd_chw_HzDequantize
deleted nodes: spconvretinanethead0_conv97_fwd_chw_HzDequantize
deleted nodes: spconvretinanethead0_conv101_fwd_chw_HzDequantize
deleted nodes: spconvretinanethead0_conv105_fwd_chw_HzDequantize
deleted nodes: spconvretinanethead0_conv109_fwd_chw_HzDequantize
```

#### The ``hb_model_modifier`` Tool

The ``hb_model_modifier`` tool is used to delete Transpose and Quantize nodes at the input end and Transpose, Dequantize, Cast, Reshape, and Softmax nodes at the output end of a ``*.bin`` model. The information of the deleted nodes is stored in the BIN model and can be viewed via ``hb_model_info``.

:::info Note
  1. The hb_model_modifier tool can only delete nodes that are directly connected to the model's input or output. If the node to be deleted is followed by other nodes, the deletion operation cannot be performed.
  2. Node names should not include special characters like ";" or "," as this may affect the tool's usage.
  3. The tool does not support processing packed models; otherwise, it will prompt: ``ERROR pack model is not supported``.
  4. Nodes to be deleted are deleted sequentially, and the model structure is updated dynamically. Before deletion, it is checked whether the node is at the model's input or output. Therefore, the deletion order is important.
:::
Since deleting specific nodes affects the input of the model, this tool is only applicable when there is only one path after the model input. As shown in the figure below, scenarios where a single input corresponds to multiple nodes are not yet supported.

![hb_model_modifier](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/hb_model_modifier.png)

- Usage

1. View deletable nodes:

```bash
  hb_model_modifier model.bin
```

2. Delete a single specified node (using node1 as an example):

```bash
  hb_model_modifier model.bin -r node1
```

3. Delete multiple specified nodes (using node1, node2, node3 as an example):

```bash
  hb_model_modifier model.bin -r node1 -r node2 -r node3
```
4. Delete nodes of a certain type (using Dequantize as an example):

```bash
  hb_model_modifier model.bin --all Dequantize
```
5. Delete nodes of multiple types (using Reshape, Cast, Dequantize as an example):

```bash
  hb_model_modifier model.bin -a Reshape -a Cast -a Dequantize
```
6. Combined usage:

```bash
  hb_model_modifier model.bin -a Reshape -a Cast -a Dequantize -r node1 -r node2 -r node3
```
- Command Line Parameters

Command line parameters for hb_model_modifier:

  --model_file<br/>
    The name of the runtime model file.

  -r<br/>
    Followed by the name of the specified node to delete. Specify multiple times if multiple nodes need to be deleted.

  -o<br/>
    Followed by the output name of the modified model (only effective when the ``-r`` parameter is present).

  -a --all<br/>
    Followed by the node type. Supports deleting all nodes of the corresponding type with one command. Specify multiple times if nodes of multiple types need to be deleted.

- Output Description

If the tool is run without any parameters, it will print out the candidate deletable nodes (i.e., all Transpose, Quantize, Dequantize, Cast, Reshape, Softmax nodes located at the input or output of the model).

Quantize nodes are used to quantize the float-type input data of the model to int8 type. Their calculation formula is as follows:

```bash
  qx = clamp(round(x / scale) + zero\_point, -128, 127)
```
``round(x)`` implements rounding of floating-point numbers. The ``clamp(x)`` function clamps the data to integer values between -128 and 127. ``zero_point`` is the zero point offset for asymmetric quantization. For symmetric quantization, ``zero_point = 0``.

A reference implementation in C++ is as follows:
```cpp
  int64_t quantized_value =
      static_cast/<int64_t/>(std::round(value / static_cast/<double/(scale)));
  quantized_value = std::min(std::max(quantized_value, min_int_value), max_int_value);
```
Dequantize nodes are used to dequantize the ``int8`` or ``int32`` type output data of the model back to ``float`` or ``double`` type. Their calculation formula is as follows:

```bash
  deqx = (x - zero\_point) * scale
```
A reference implementation in C++ is as follows:

```cpp
  static_cast/<float/>(value) * scale
```
:::info Note

  The tool currently supports deleting:

  1. Nodes at the input end that are Quantize or Transpose nodes.
  2. Nodes at the output end that are Transpose, Dequantize, Cast, Reshape, or Softmax nodes.
:::

The tool's output is as follows:

```bash
hb_model_modifier resnet50_64x56x56_featuremap.bin
2022-04-21 18:22:30,207 INFO Nodes that can be deleted: ['data_res2a_branch1_HzQuantize_TransposeInput0', 'fc1000_reshape_0']
```
After specifying the ``-r`` option, the tool will print the type of the node in the model, the node information stored in the bin file, and inform you that the specified node has been deleted:

```bash
hb_model_modifier resnet50_64x56x56_featuremap.bin -r data_res2a_branch1_HzQuantize_TransposeInput0
Node 'data_res2a_branch1_HzQuantize_TransposeInput0' found, its OP type is 'Transpose'
Node 'data_res2a_branch1_HzQuantize_TransposeInput0' is removed
modified model saved as resnet50_64x56x56_featuremap_modified.bin
```
You can then use the ``hb_model_info`` tool to view the information of deleted nodes. The names of the deleted nodes will be printed at the end of the output, and a ``deleted_nodes_info.txt`` file will be generated. Each line in the file records the initial information of the corresponding deleted node. The printout of the deleted node names is shown below:

```bash
hb_model_info resnet50_64x56x56_featuremap_modified.bin
Start hb_model_info....
hb_model_info version 1.7.0
********* resnet50_64x56x56_featuremap info *********
...
--------- deleted nodes -
deleted nodes: data_res2a_branch1_HzQuantize_TransposeInput0
```

#### The ``hb_model_verifier`` Tool

The ``hb_model_verifier`` tool is used to verify the results of a specified fixed-point model and runtime model. This tool uses a specified image to perform inference on the fixed-point model, inference on the runtime model on the board and on the x86-side emulator, and inference on the runtime model on the board (if the given IP is pingable and ``hrt_tools`` is installed on the board; otherwise, you can use the ``install.sh`` script under ``package/board`` in the toolchain SDK package for installation). Inference on the runtime model on the x86 side (ensure ``hrt_tools`` is installed on the host side; otherwise, you can use the ``install.sh`` script under ``package/host`` in the toolchain SDK package for installation). It then compares the results from the three parties pairwise and gives a pass/fail conclusion. If no image is specified, the tool will use a default image for inference (for featuremap models, random tensor data will be generated).

:::caution Note
  For information on how to obtain the ``package`` materials, please refer to the [**Deliverables Description**](../intermediate/environment_config.md#deliverable-usage-instructions).
:::
- Usage

```bash
  hb_model_verifier -q ${quanti_model} \
                    -b ${bin_model} \
                    -a ${board_ip} \
                    -i ${input_img} \
                    -d ${digits}
```
- Command Line Parameters

Command line parameters for hb_model_verifier:

  -quanti_model, -q<br/>
    The name of the fixed-point model.

  --bin_model, -b<br/>
    The name of the bin model.

  --arm-board-ip, -a<br/>
    The IP address of the ARM board used for on-board testing.

  --input-img, -i<br/>
    The image used for inference testing. If not specified, a default image or random tensor will be used. Binary image files must have the ``.bin`` suffix.

  --compare_digits, -d<br/>
    Compares the numerical precision of the inference results; if not specified, defaults to comparing up to five decimal places.

- Output Description

The result comparison is ultimately displayed in the terminal. The tool compares the results of the ONNX model execution, the emulator execution, and the on-board results pairwise. If there are no issues, it should display the following:

```bash
  Quanti onnx and Arm result Strict check PASSED
```
When the accuracy of the fixed-point model and the runtime model is inconsistent, specific information about the inconsistencies will be output.

``mismatch line num`` is the number of results with inconsistent accuracy between the two models, including three types of inconsistencies: 
``mismatch.line_miss num`` is the number of results where the output count is inconsistent; 
``mismatch.line_diff num`` is the number of results where the output difference is too large; 
``mismatch.line_nan num`` is the number of results where the output is NaN. 

``total line num`` is the total number of output data points. 

``mismatch rate`` is the proportion of inconsistent data points to the total number of output data points.

```bash
  INFO mismatch line num: 39
  INFO ****************************
  INFO mismatch.line_miss num: 0
  INFO mismatch.line_diff num: 39
  INFO mismatch.line_nan num: 0
  INFO ****************************
  INFO total line num: 327680
  INFO mismatch rate: 0.0001190185546875
```
:::caution Note

  1. ``hb_model_verifier`` currently only supports single-input models.
  2. If the model has multiple outputs, only the result of the first output will be compared.
  3. Verification of packed *.bin models is currently not supported; otherwise, the console will produce the following prompt:
:::

```bash
  ERROR pack model is not supported
```

#### The ``hb_eval_preprocess`` Tool {#hb_eval_preprocess}

Used to preprocess image data in an x86 environment when evaluating model accuracy. Preprocessing refers to specific operations performed on image data before it is fed into the model, such as image resizing, cropping, and padding.

- Usage
```
  hb_eval_preprocess [OPTIONS]
```
- Command Line Parameters

Command line parameters for hb_eval_preprocess:

  --version<br/>
    Displays the version and exits.

  -m, --model_name<br/>
    Sets the model name. The range of supported models can be viewed via ``hb_eval_preprocess --help``.

  -i, --image_dir<br/>
    The path to the input images.

  -o, --output_dir<br/>
    The output path.

  -v, --val_txt<br/>
    Sets the file name of the images required for evaluation. The preprocessed images will correspond to the image names in this file.

  -h, --help<br/>
    Displays help information.

- Output Description

The ``hb_eval_preprocess`` command will generate image binary files in the path specified by ``--output_dir``.

:::tip Tip
  For more examples of using the ``hb_eval_preprocess`` tool in on-board model accuracy evaluation, please refer to the [**Data Preprocessing**](./runtime_sample.md#data_preprocess) section in the "Public Model Evaluation Guide" of the Embedded Application Development documentation.
:::