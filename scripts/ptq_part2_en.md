
**mean_value Parameter Description**

- **Purpose**: This parameter specifies the mean value subtracted from the image in the specified preprocessing method.

- **Usage**: Configure this parameter when ``norm_type`` is set to ``data_mean_and_scale`` or ``data_mean``.

- **Description**:

  - When there is only one input node, configure a single value, meaning all channels subtract this mean.
  - When there are multiple nodes, provide values equal in number to the channels (separated by spaces), meaning each channel subtracts a different mean.

:::caution Note

  1. The number of configured input nodes must match the number of nodes configured in ``norm_type``.
  2. If a node does not require ``mean`` processing, configure ``'None'`` for that node.
:::

**scale_value Parameter Description**

- **Purpose**: This parameter specifies the scale coefficient for the specified preprocessing method.

- **Usage**: Configure this parameter when ``norm_type`` is set to ``data_mean_and_scale`` or ``data_scale``.

- **Description**:

  - When there is only one input node, configure a single value, meaning all channels are multiplied by this coefficient.
  - When there are multiple nodes, provide values equal in number to the channels (separated by spaces), meaning each channel is multiplied by a different coefficient.

:::caution Note

  1. The number of configured input nodes must match the number of nodes configured in ``norm_type``.
  2. If a node does not require ``scale`` processing, configure ``'None'`` for that node.
:::

**Calculation Formulas and Example Description**

- Data standardization calculation formula during model training

The mean and scale parameters in the yaml file need to be converted from the mean and std used during training.

The data standardization operation in the preprocessing node (i.e., the calculation formula in the HzPreprocess node) is `norm\_data = ( data − mean ) * scale`.

Taking yolov3 as an example, its preprocessing code during training is:

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

Rewritten in the HzPreprocess node calculation form: `norm\_data= (\frac{data}{255}  −𝑚𝑒𝑎𝑛) * \frac{1}{𝑠𝑡𝑑} =(data−255𝑚𝑒𝑎𝑛) * \frac{1}{255𝑠𝑡𝑑}` ,

Therefore: `mean\_yaml = 255 mean、𝑠𝑐𝑎𝑙𝑒\_𝑦𝑎𝑚𝑙=  \frac{1}{255 𝑠𝑡𝑑}` .

- Calculation formula during model inference

Based on the configuration parameters in the yaml configuration file, the tool decides whether to add an HzPreprocess node.
When mean/scale is configured, an HzPreprocess node is added at the input during model conversion. The HzPreprocess node can be understood as performing a conv operation on the input data.

The calculation formula inside HzPreprocess is: `((input（value range [-128,127]）+ 128) - mean) * scale`, where ``weight=scale`` and ``bias=(128-mean) * scale`` .

:::caution Note

  1. After adding mean/scale in the yaml, you do not need to add MeanTransformer and ScaleTransformer in the preprocessing pipeline.
  2. Adding mean/scale in the yaml places the parameters inside the HzPreprocess node, which is a BPU node.
:::

#### Conversion Internal Process Interpretation{#conversion_interpretation}

The model conversion stage completes the conversion from a floating-point model to a D-Robotics hybrid heterogeneous model. To enable this heterogeneous model to run quickly and efficiently on embedded devices, model conversion focuses on solving two key problems: **input data processing** and **model optimization and compilation**. This section covers these two key topics in order.

**Input Data Processing** The D-Robotics X3 processor provides hardware-level support for certain types of model input paths.
For example, in the video pipeline, the video processing subsystem provides image cropping, scaling, and other image quality optimization functions for image acquisition. The output of these subsystems is YUV420 NV12 format images,
while algorithm models are often trained based on common image formats such as bgr/rgb.

The solution D-Robotics provides for this situation is:

- 1. Each converted model provides two descriptions: one describes the input data of the original floating-point model ( ``input_type_train`` and ``input_layout_train`` ), and the other describes the input data we need to interface with the processor ( ``input_type_rt`` and ``input_layout_rt`` ).

- 2. mean/scale operations on image data are also common, but processor-supported data formats such as YUV420 NV12 are not suitable for such operations. Therefore, we also embed these common image preprocessing operations into the model.

After the above two processing methods, the input part of the ``***.bin`` heterogeneous model produced during model conversion will be in the state shown in the figure below.

![input_data_process](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/input_data_process.png)

The data layouts in the figure above are only NCHW and NHWC. N represents batch size, C represents channel, H represents height, and W represents width.
The two different layouts reflect different memory access characteristics. NHWC is more commonly used in TensorFlow models, while Caffe uses NCHW throughout,
The D-Robotics processor does not restrict the data layout used, but has two requirements: first, ``input_layout_train`` must be consistent with the data layout of the original model; second, prepare data on the processor with a layout consistent with ``input_layout_rt``. Correct data layout is the foundation for successful data parsing.

The model conversion tool automatically adds data conversion nodes based on the data formats specified by ``input_type_rt`` and ``input_type_train``. Based on D-Robotics practical experience,
not every type combination is needed. To avoid misuse, we only expose some fixed type combinations, as shown in the table below:

  | ``input_type_train`` \\ ``input_type_rt`` | nv12 | yuv444 | rgb | bgr | gray | featuremap |
  |-------|------|--------|-----|-----|------|------------|
  | yuv444                                    | Y    | Y      | N   | N   | N    | N          |
  | rgb                                       | Y    | Y      | Y   | Y   | N    | N          |
  | bgr                                       | Y    | Y      | Y   | Y   | N    | N          |
  | gray                                      | N    | N      | N   | N   | Y    | N          |
  | featuremap                                | N    | N      | N   | N   | N    | Y          |
:::info Note

  The first row in the table lists the types supported in ``input_type_rt``, and the first column lists the types supported in ``input_type_train``.
  **Y/N** indicates whether the corresponding conversion from ``input_type_rt`` to ``input_type_train`` is supported.
  In the final bin model produced by model conversion, the conversion from ``input_type_rt`` to ``input_type_train`` is an internal process.
  You only need to focus on the data format of ``input_type_rt``.
  **Correctly understanding the requirements of each** ``input_type_rt`` **format is important for preparing inference data in embedded applications. The following describes each**
  ``input_type_rt`` **format:**

  - rgb, bgr, and gray are common image formats. Note that each value is represented as UINT8.
  - yuv444 is a common image format. Note that each value is represented as UINT8.
  - nv12 is a common yuv420 image format. Each value is represented as UINT8.
  - A special case for nv12 is when ``input_space_and_range`` is set to ``bt601_video``
    (refer to the earlier introduction of the ``input_space_and_range`` parameter). Compared with the regular nv12 case, its value range changes from [0,255] to [16,235],
    while each value is still represented as UINT8.
  - For featuremap input models, the data type only requires your data to be four-dimensional, with each value represented as float32. For example, radar and speech models commonly use this format.
:::

:::tip Tip

  Calibration data only needs to be processed to input_type_train. Also note **do not perform duplicate norm operations**.

  The above ``input_type_rt`` and ``input_type_train`` are embedded in the algorithm toolchain processing flow. If you are certain that conversion is not needed,
  you can set both ``input_type`` configurations to the same value, so ``input_type`` will be passed through directly without affecting the actual execution performance of the model.

  Similarly, data preprocessing is also embedded in the flow. If you do not need any preprocessing, disable this function through ``norm_type`` configuration without affecting the actual execution performance of the model.
:::

**Model Optimization and Compilation** completes several important stages: model parsing, model optimization, model calibration and quantization, and model compilation. The internal workflow is shown in the figure below.

![model_optimization](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/model_optimization.png)

:::info Note

  1. ``input_type_rt*`` represents the intermediate format of input_type_rt.
  
  2. The X3 processor architecture only supports inference with ``NHWC`` data. Use the visualization tool Netron to check the data layout of the input nodes in ``quantized_model.onnx`` and decide whether to add ``layout conversion`` in preprocessing.
:::

**Model Parsing Stage** For Caffe floating-point models, conversion to ONNX floating-point models is completed.
Based on the configuration parameters in the conversion yaml file, the tool decides whether to add data preprocessing nodes to the original floating-point model. This stage produces an original_float_model.onnx.
This ONNX model still has float32 computation precision, but a data preprocessing node has been added at the input.

Ideally, this preprocessing node should complete the full conversion from ``input_type_rt`` to ``input_type_train``.
In practice, the entire type conversion process is completed in cooperation with D-Robotics processor hardware, and the ONNX model does not include the hardware conversion part.
Therefore, the actual input type of the ONNX model uses an intermediate type, which is the result type after hardware processing of ``input_type_rt``,
and the data layout (NCHW/NHWC) remains consistent with the input layout of the original floating-point model.
Each ``input_type_rt`` has a specific corresponding intermediate type, as shown in the table below:

  | **nv12**   | **yuv444** | **rgb** | **bgr** | **gray** | featuremap |
  |------------|------------|---------|---------|----------|------------|
  | yuv444_128 | yuv444_128 | RGB_128 | BGR_128 | GRAY_128 | featuremap |

:::info Note

  The bold part in the first row of the table is the data type specified by ``input_type_rt``. The second row is the intermediate type corresponding to the specific ``input_type_rt``,
  which is the input type of original_float_model.onnx. Each type is explained as follows:

  - yuv444_128 is yuv444 data minus 128, with each value represented as int8.
  - RGB_128 is RGB data minus 128, with each value represented as int8.
  - BGR_128 is BGR data minus 128, with each value represented as int8.
  - GRAY_128 is gray data minus 128, with each value represented as int8.
  - featuremap is a four-dimensional tensor, with each value represented as float32.
:::

**Model Optimization Stage** implements operator optimization strategies applicable to the D-Robotics platform, such as fusing BN into Conv.
The output of this stage is an optimized_float_model.onnx. This ONNX model still has float32 computation precision, and optimization does not affect the model computation results.
The input data requirements of the model remain the same as the previous original_float_model.

**Model Calibration Stage** uses the calibration data you provide to calculate the necessary quantization threshold parameters. These parameters are fed directly into the quantization stage and do not produce a new model state.

**Model Quantization Stage** completes model quantization using the parameters obtained from calibration. The output of this stage is a quantized_model.onnx.
This model already has int8 computation precision. Using this model, you can evaluate the accuracy loss caused by model quantization.
This model requires the basic data format and layout of the input to remain the same as ``original_float_model``, but the layout and numeric representation have changed.
The overall input changes compared with ``original_float_model`` are described as follows:

- Data layout on ``RDK X3`` uses NHWC.
- When ``input_type_rt`` is not ``featuremap``, the input data type uses INT8.
  Conversely, when ``input_type_rt`` is ``featuremap``, the input data type is float32.

The layout correspondence is as follows:

- Original model input layout: NCHW.
- input_layout_train: NCHW.
- origin.onnx input layout: NCHW.
- calibrated_model.onnx input layout: NCHW.
- quanti.onnx input layout: NHWC.

That is: the input layout of input_layout_train, origin.onnx, and calibrated_model.onnx is consistent with the original model input layout.

:::caution Note
  Please note that when input_type_rt is nv12, the input layout of the corresponding quanti.onnx is NHWC.
:::

**Model Compilation Stage** uses the D-Robotics model compiler to convert the quantized model into computation instructions and data supported by the D-Robotics platform.
The output of this stage is a ``***.bin`` model, which is the model that can run on D-Robotics embedded platforms and is the final output of model conversion.


#### Conversion Result Interpretation
This section introduces how to interpret a successful model conversion and how to analyze an unsuccessful conversion.
To confirm successful model conversion, you need to verify three aspects: ``makertbin`` status information, similarity information, and `working_dir` output.
For ``makertbin`` status information, a successful conversion will give a clear message at the end of the console output as follows:

```bash
  2021-04-21 11:13:08,337 INFO Convert to runtime bin file successfully!
  2021-04-21 11:13:08,337 INFO End Model Convert
```
Similarity information is also in the ``makertbin`` console output, before the ``makertbin`` status information, in the following form:

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

In the output listed above, Node, ON, Subgraph, and Type are interpreted the same way as the ``hb_mapper checker`` tool.
Please refer to the earlier [**Check Result Interpretation**](#check_result) section;
Threshold is the calibration threshold for each layer, used for feedback to D-Robotics technical support in abnormal situations. Under normal circumstances, it does not need attention;
The Cosine Similarity column reflects the cosine similarity between the outputs of the original floating-point model and the quantized model for the operator corresponding to the Node column.

:::tip Tip

  In general, **if the Cosine Similarity of the model output nodes is >= 0.99, the model quantization can be considered normal**. If the similarity of output nodes is below 0.8, there is noticeable accuracy loss. Of course, Cosine Similarity only indicates one reference for data stability after quantization and does not have an obvious direct correlation with model accuracy impact.
  For fully accurate accuracy assessment, please read the content in [**Model Accuracy Analysis and Tuning**](#accuracy_evaluation).
:::

Conversion output is stored in the path specified by the ``working_dir`` conversion configuration parameter. After successful model conversion,
you can obtain the following files in that directory (the \*\*\* part is what you specify through the ``output_model_file_prefix`` conversion configuration parameter):

- \*\*\*_original_float_model.onnx
- \*\*\*_optimized_float_model.onnx
- \*\*\*_calibrated_model.onnx
- \*\*\*_quantized_model.onnx
- \*\*\*.bin

[**Conversion Output Interpretation**](#conversion_output) introduces the purpose of each output.

:::caution Note
  Before on-board deployment, we recommend completing the model performance and accuracy evaluation process introduced in [**Model Performance Analysis and Tuning**](#performance_evaluation) to avoid extending model conversion issues to the subsequent embedded stage.
:::

If any of the three aspects for verifying successful model conversion is missing, it indicates that model conversion encountered an error.
In general, the ``makertbin`` tool outputs error information to the console when an error occurs.
For example, if we do not configure the ``prototxt`` and ``caffe_model`` parameters in the yaml file during Caffe model conversion, the model conversion tool gives the following message.

```bash
2021-04-21 14:45:34,085 ERROR Key 'model_parameters' error:
Missing keys: 'caffe_model', 'prototxt'
2021-04-21 14:45:34,085 ERROR yaml file parse failed. Please double check your input
2021-04-21 14:45:34,085 ERROR exception in command: makertbin
```
If the console log information cannot help you identify the problem, please refer to the [**Model Quantization Errors and Solutions**](../../../08_FAQ/05_toolchain.md#model_convert_errors_and_solutions) section. If the above steps still cannot resolve the issue, contact the D-Robotics technical support team or post your question on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc/). We will provide support within 24 hours.


#### Conversion Output Interpretation{#conversion_output}

As mentioned above, the outputs of a successful model conversion include the following four parts. This section introduces the purpose of each output:

- \*\*\*_original_float_model.onnx
- \*\*\*_optimized_float_model.onnx
- \*\*\*_calibrated_model.onnx
- \*\*\*_quantized_model.onnx
- \*\*\*.bin

The production process of \*\*\*_original_float_model.onnx can be found in the introduction in [**Conversion Internal Process Interpretation**](#conversion_interpretation).
The computation precision of this model is exactly the same as the original floating-point model used as conversion input. An important change is that some data preprocessing computation has been added to adapt to the D-Robotics platform (a preprocessing operator node ``HzPreprocess`` has been added. You can open the onnx model with the netron tool to view it. For details about this operator, see [**Preprocessing HzPreprocess Operator Description**](#pre_process)).
In general, you do not need to use this model. If the conversion result is abnormal and the troubleshooting methods introduced above still cannot solve your problem, providing this model to the D-Robotics technical support team or posting your question on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc/) will help you resolve the issue quickly.

The production process of \*\*\*_calibrated_model.onnx can be found in the introduction in [**Conversion Internal Process Interpretation**](#conversion_interpretation).
This model is an intermediate product obtained after the model conversion toolchain optimizes the floating-point model structure, calculates the quantization parameters corresponding to each node using calibration data, and saves them in calibration nodes.

The production process of \*\*\*_optimized_float_model.onnx can be found in the introduction in [**Conversion Internal Process Interpretation**](#conversion_interpretation).
This model undergoes some operator-level optimization operations, commonly operator fusion.
Through visual comparison with the original_float model, you can clearly see some operator structure-level changes, but these do not affect the model computation precision.
In general, you do not need to use this model. If the conversion result is abnormal and the troubleshooting methods introduced above still cannot solve your problem, providing this model to the D-Robotics technical support team or posting your question on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc/) will help you resolve the issue quickly.

The production process of \*\*\*_quantized_model.onnx can be found in the introduction in [**Conversion Internal Process Interpretation**](#conversion_interpretation).
This model has completed the calibration and quantization process. To evaluate the accuracy loss of the quantized model, read the model accuracy analysis and tuning content below.
This model must be used during accuracy verification. For specific usage, please refer to the introduction in [**Model Accuracy Analysis and Tuning**](#accuracy_evaluation).

\*\*\*.bin is the model that can be loaded and run on D-Robotics processors.
Together with the content introduced in the on-board runtime application development guide section,
you can quickly deploy and run the model on D-Robotics processors. However, to ensure that the model performance and accuracy meet your expectations,
we recommend completing the performance and accuracy analysis processes introduced in [**Model Conversion**](#model_conversion) and [**Model Accuracy Analysis and Tuning**](#accuracy_evaluation)
before proceeding to application development and deployment.

:::caution Note

  Usually, after the model conversion stage is completed, you can obtain a model that runs on D-Robotics processors. However, to ensure that the model performance and accuracy meet application requirements, D-Robotics recommends completing the subsequent performance evaluation and accuracy evaluation steps after each conversion.

  The model conversion process generates onnx models. These models are intermediate products intended to help users verify model accuracy, so compatibility across versions is not guaranteed. When using the evaluation scripts in the examples to evaluate onnx models on a single image or on a test set, please use onnx models regenerated with the current version of the tools.
:::

### Model Performance Analysis{#performance_evaluation}

This section introduces how to use the tools provided by D-Robotics to evaluate model performance. Using these tools, you can obtain performance results that are largely consistent with actual on-board execution. If the evaluation results do not meet expectations, we recommend resolving performance issues according to the optimization suggestions provided by D-Robotics, and not extending model performance issues to the application development stage.

#### Performance Evaluation on Development Machine{#hb_perf}

Use the ``hb_perf`` tool to evaluate model performance as follows:

```bash
  hb_perf  ***.bin
```
:::info Note
  If analyzing a model after ``pack``, add a ``-p`` parameter. The command is ``hb_perf -p ***.bin``.
  For model ``pack``, please refer to the introduction in the Other Model Tools (Optional) section.
:::

The \*\*\*.bin in the command is the fixed-point model generated in the model conversion step. After the command completes, an `hb_perf_result` folder is generated in the current directory containing the specific model analysis results.
The following is the evaluation result of the example model MobileNetv1:

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
Open the ``mobilenetv1_224x224_nv12.html`` main page in a browser. Its content is shown in the figure below:

![hb_mapper_perf_2](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/hb_mapper_perf_2.png)

The analysis results mainly consist of three parts: Model Performance Summary, Details, and BIN Model Structure.
Model Performance Summary is the overall performance evaluation result of the bin model. The metrics are:

- Model Name——Model name.
- Model Latency(ms)——Overall single-frame computation latency of the model (in ms).
- Total DDR (loaded+stored) bytes per frame(MB per frame)——Total DDR usage for data loading and storage in the BPU part of the model (in MB/frame).
- Loaded Bytes per Frame——Data read per frame during model execution.
- Stored Bytes per Frame——Data stored per frame during model execution.

The BIN Model Structure section provides subgraph-level visualization of the bin model. Dark cyan nodes in the figure represent nodes running on the BPU, and gray nodes represent nodes computed on the CPU.

When viewing Details and BIN Model Structure, you need to understand the concept of subgraph.
If CPU-computed operators appear in the model network structure, the model conversion tool splits the consecutive BPU computation parts before and after the CPU operator into two independent subgraphs.
For details, refer to the introduction in the [**Model Verification**](#model_check) section.

Details provides specific information for each BPU subgraph of the model. In the ``mobilenetv1_224x224_nv12.html`` main page, the subgraph metrics are:

- Model Subgraph Name——Subgraph name.
- Model Subgraph Calculation Load (OPpf)——Single-frame computation load of the subgraph.
- Model Subgraph DDR Occupation(Mbpf)——Single-frame read/write data volume of the subgraph (in MB).
- Model Subgraph Latency(ms)——Single-frame computation latency of the subgraph (in ms).

Each subgraph result provides detailed reference information.

:::caution Note

  The reference information page differs depending on whether debug configuration is enabled.
  The Layer Details in the figure below can only be obtained when the ``debug`` parameter is set to ``True`` in the yaml configuration file.
  For how to configure this ``debug`` parameter, please refer to the introduction in the [**Using the hb_mapper makertbin Tool to Convert Models**](#makertbin) section.
:::
Layer Details provides operator-level analysis and can be used as a reference during model debugging and analysis. For example, if certain BPU operators cause low model performance, the analysis results help you locate the specific operators.

![layer_details](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/layer_details.png)

:::caution Note
  The analysis results of the ``hb_perf`` tool help you understand the subgraph structure of the bin model and the static analysis metrics of the BPU computation part in the model. Note that the analysis results do not include CPU computation evaluation. If you need CPU computation performance, please measure model performance on the development board.
:::

#### On-Board Performance Measurement


To quickly evaluate model performance on the development board, use the ``hrt_model_exec perf`` tool, which can directly evaluate model inference performance and obtain model information on the development board.

Before using the ``hrt_model_exec perf`` tool, please prepare:

1. Ensure you have completed development board system updates by referring to the system update section.

2. Copy the bin model obtained on the Ubuntu development machine to the development board (recommended in the /userdata directory).
   The development board runs a Linux system. You can use common Linux methods such as ``scp`` to complete this copy process.

The ``hrt_model_exec perf`` tool command is as follows (**note: execute on the development board**):

```bash
./hrt_model_exec perf --model_file mobilenetv1_224x224_nv12.bin \
                      --model_name="" \
                      --core_id=0 \
                      --frame_count=200 \
                      --perf_time=0 \
                      --thread_num=1 \
                      --profile_path="."
```
hrt_model_exec perf parameter description:

  model_file：<br/>
    Name of the bin model whose performance needs to be analyzed.

  model_name:<br/>
    Name of the bin model whose performance needs to be analyzed. If ``model_file`` contains only one model, this can be omitted.

  core_id:<br/>
    Default ``0``. Core id used to run the model. ``0`` represents any core, ``1`` represents core 0, ``2`` represents core 1. To analyze the dual-core maximum frame rate, set this to ``0``.

  frame_count：<br/>
    Default ``200``. Sets the number of inference frames. The tool executes the specified number of times before analyzing average latency. Takes effect when ``perf_time`` is ``0``.

  perf_time:<br/>
    Default ``0``, in minutes. Sets the inference duration. The tool executes for the specified time before analyzing average latency.

  thread_num：<br/>
    Default ``1``. Sets the number of running threads. Value range ``[1,8]``. To analyze the maximum frame rate, increase the thread count.

  profile_path：<br/>
    Disabled by default. Path where statistical tool logs are generated. Analysis results introduced by this parameter are stored in profiler.log and profiler.csv files in the specified directory.

The following example shows on-board measurement results on the **RDK X3** development board. After the command completes, you will get the following log on the console:

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
  In the evaluation results, ``Average latency`` and ``Frame rate`` represent average single-frame inference latency and maximum model frame rate, respectively.
  To obtain the maximum frame rate of the model running on the board, try adjusting the value of ``thread_num`` and find the optimal thread count. Different values produce different performance results.
:::

The information on the console only shows the overall situation. The node_profiler.log file generated by setting the ``profile_path`` parameter records richer model performance information:

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
The log content above corresponds to the bin visualization diagram introduced in the BIN Model Structure section in [**Using the hb_perf Tool to Estimate Performance**](#hb_perf).
Each node in the diagram has a corresponding node in the profiler.log file, which can be matched by ``name``. In addition, profiler.log records the execution time of each node, providing a reference for optimizing model operators. Because BPU nodes in the model have special requirements for input and output, such as special layout and padding alignment requirements, input and output data of BPU nodes need to be processed.

- ``Preprocess``: Represents padding and layout conversion operations on model input data. The latency is counted in Preprocess.
- ``xxxx_input_layout_convert``: Represents padding and layout conversion operations on BPU node input data. The latency is counted in xxxx_input_layout_convert.
- ``xxxx_output_layout_convert``: Represents removing padding and layout conversion operations on BPU node output data. The latency is counted in xxxx_output_layout_convert.
``profiler`` analysis is a common operation in model performance tuning. The earlier [**Check Result Interpretation**](#check_result) section mentioned that CPU operators do not need much attention during the check stage. At this stage, you can see the specific latency of CPU operators and perform model performance tuning based on the latency of the corresponding operators.

:::tip Tip

  If model latency is severe, you can also try the following methods for performance optimization:
  1. Single-frame single-core: One frame of data comes in, and the model is run for inference on one core;
  2. Single-frame dual-core: The model is specified as a dual-core model at compile time (core_num: 2 in the yaml configuration file). After running, it automatically occupies resources on both cores. One frame of data comes in, is split into two parts for separate computation, and then combined. This mode shows noticeable optimization effects mainly on some large models, reducing latency to some extent. Small models may actually become slower due to dual-core scheduling;
  3. Dual-frame dual-core: Each core runs one model independently, processing its own data frames. Latency will not decrease, but the frame rate can reach approximately 2x
:::



#### Model Performance Optimization

Based on the performance analysis results above, you may find that model performance does not meet expectations. This section introduces D-Robotics recommendations and measures for improving model performance, including checking yaml configuration parameters, handling CPU operators, high-performance model design recommendations, and using D-Robotics platform-friendly structures and models.

:::caution Note
  Some modification suggestions in this section may affect the parameter space of the original floating-point model, so you need to retrain the model. To avoid repeatedly adjusting and training the model during performance tuning, we recommend using randomly initialized parameters to export a model to verify performance before achieving satisfactory model performance.
:::

##### Check yaml Parameters That Affect Model Performance

In the yaml configuration file for model conversion, some parameters actually affect the final model performance. First check whether they are configured correctly according to model expectations.
For the specific meaning and purpose of each parameter, please refer to the [**Compiler Parameter Group**](#compiler_parameters) section.

- ``layer_out_dump``: Specifies whether to output intermediate results of the model during model conversion. Generally used only for debugging.
  If configured as ``True``, a dequantization output node is added for each convolution operator, which significantly reduces on-board model performance.
  Therefore, when evaluating performance, be sure to configure this parameter as ``False``.
- ``compile_mode``: Selects whether the optimization direction during model compilation is bandwidth or latency. When focusing on performance, configure it as ``latency``.
- ``optimize_level``: Selects the compiler optimization level. In actual use, configure it as ``O3`` for best performance.
- ``core_num``:**Note:** This parameter applies only to **RDK X3**. When configured as ``2``, both cores can be invoked simultaneously to run the model, reducing single-frame inference latency, but it also affects overall throughput.
- ``debug``: Configuring as ``True`` enables the compiler debug mode, which can output performance simulation-related information such as frame rate and DDR bandwidth usage.
  Generally used during the performance evaluation stage. For product delivery, this parameter can be disabled to reduce model size and improve model execution efficiency.
- ``max_time_per_fc``: Controls the execution duration of function-call data instructions in the compiled model, enabling model priority preemption.
  Changing the function-call execution duration of the preempted model with this parameter affects the on-board performance of that model.

##### Handle CPU Operators

Based on evaluation with the ``hrt_model_exec perf`` tool, if you can confirm that the model performance bottleneck is caused by CPU operators, we recommend checking the content in [**Model Operator Support List**](./supported_op_list) to confirm whether the operators currently running on the CPU have BPU support capability.

If the operator has BPU support capability in the model operator support list, the operator parameters likely exceed the BPU-supported parameter constraint range. We recommend adjusting the corresponding original floating-point model computation parameters to within the constraint range.
To quickly identify the specific parameters that exceed the constraints, we recommend using the method introduced in the [**Model Verification**](#model_check) section to perform another check. The tool will directly provide prompts for parameters exceeding the BPU support range.

:::info Note
  You need to control the impact of modifying original floating-point model parameters on model computation accuracy. For example, when Convolution ``input_channel`` or ``output_channel`` exceeds the range, it is a typical case. Reducing channels enables BPU support for that operator, but this single modification may also affect model accuracy.
:::

If the operator does not have BPU support capability, you need to perform corresponding optimization operations according to the following situations:

- CPU operator in the middle of the model

  For CPU operators in the middle of the model, we recommend first trying parameter adjustment, operator replacement, or model modification.

- CPU operator at the beginning or end of the model

  For CPU operators at the beginning or end of the model, please refer to the following examples. Quantize/dequantize nodes are used as an example below:

  - For nodes connected to model inputs and outputs, you can add the ``remove_node_type`` parameter in the model_parameters configuration group (model parameter group) in the yaml file and recompile the model.

    ```bash

      remove_node_type: "Quantize; Dequantize"
    ```

    Or use the hb_model_modifier tool to modify the bin model:

    ```bash

      hb_model_modifier x.bin -a Quantize -a Dequantize
    ```

  - For models like the one in the figure below that do not have nodes connected to input and output nodes, use the hb_model_modifier tool to determine whether connected nodes support deletion, then delete them one by one in order.

    ![nodes_connected](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/nodes_connected.png)

    First use the hb_perf tool to obtain the model structure diagram, then use the following two commands to remove Quantize nodes from top to bottom.
    For Dequantize nodes, remove them one by one from bottom to top. The name of each node that can be deleted at each step can be viewed with ``hb_model_modifier x.bin``.

    ```bash

      hb_model_modifier x.bin -r res2a_branch1_NCHW2NHWC_LayoutConvert_Input0
      hb_model_modifier x_modified.bin -r data_res2a_branch1_HzQuantize
    ```


##### High-Performance Model Design Recommendations

Based on performance evaluation results, the CPU latency proportion may be very small. In that case, the model performance bottleneck is long BPU inference time.
When this occurs, it indicates that the model is already using all BPU computation resources. The next step is to improve computation resource utilization for performance optimization.
Because each processor has its own hardware characteristics, whether the computation parameters of an algorithm model align well with the corresponding hardware characteristics directly determines the model computation resource utilization. The higher the alignment, the higher the utilization, and vice versa.

This section focuses on the hardware characteristics of D-Robotics processors: D-Robotics provides processors designed to accelerate CNNs (convolutional neural networks). Most computation resources are concentrated on processing various convolution computations. We recommend that your model be convolution-dominant, because operators other than convolution reduce computation resource utilization, with different OPs causing varying degrees of performance impact.

- **Other Recommendations**

  The computation efficiency of ``depthwise convolution`` on D-Robotics processors is close to 100%, so for ``MobileNet-class`` models, the BPU has an efficiency advantage.

  When designing your model, try to reduce the input and output dimensions of the BPU segment of the model to reduce the latency of quantize and dequantize nodes and hardware bandwidth pressure.
  Taking a typical segmentation model as an example, we recommend integrating the Argmax operator directly into the model itself. Note that Argmax supports BPU acceleration only when the following conditions are met:

    1. In Caffe, the Softmax layer defaults to axis=1, while the ArgMax layer defaults to axis=0. Keep axis consistent when replacing operators.
    2. The Channel of Argmax must be less than or equal to 64; otherwise it can only be computed on the CPU.

- **BPU-Oriented High-Efficiency Model Optimization**

  The BPU of D-Robotics processors has targeted optimizations for ``Depthwise Convolution`` and ``Group Convolution``. Therefore, we recommend using MobileNetv2 and EfficientNet_lite with Depthwise+Pointwise structure, as well as VarGNet manually designed by D-Robotics based on GroupConv, as model backbones to achieve higher performance gains.

  More model structures and business models are under continuous exploration. We will provide more models as direct references, and these outputs will be updated periodically at https://github.com/D-Robotics/rdk_model_zoo .
  If the above still cannot meet your needs, feel free to post on the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc) to contact us. We will provide more targeted guidance based on your specific problem.


### Model Accuracy Analysis{#accuracy_evaluation}

The PTQ post-training quantization approach that converts floating-point models to fixed-point models based on dozens or hundreds of calibration images inevitably incurs some accuracy loss.
The D-Robotics PTQ conversion tool, validated through extensive practical experience, can keep model accuracy loss within ``1%`` in most cases when selecting the optimal quantization parameter combination.

This section first introduces how to perform model accuracy analysis correctly. If evaluation shows results below expectations, refer to the **Accuracy Tuning** subsection for model accuracy tuning.

#### Accuracy Analysis

As mentioned earlier, the outputs of a successful model conversion include the following four parts:

- \*\*\*_original_float_model.onnx
- \*\*\*_optimized_float_model.onnx
- \*\*\*_quantized_model.onnx
- \*\*\*.bin

Although the final bin model is the one deployed on D-Robotics processors, for convenience in quickly obtaining model accuracy on Ubuntu/CentOS development machines, we also support using \*\*\*_quantized_model.onnx to complete model accuracy testing. The \*\*\*_quantized_model.onnx quantized model and the bin model running on X3 have consistent accuracy effects.

We recommend using the D-Robotics development library to load the ONNX model for inference. The basic flow is shown below:

:::caution Note
  1. The example code applies not only to quantized models, but also to original and optimized models. Prepare data according to the input type and layout requirements of different models for model inference.

  2. We recommend referring to the accuracy verification methods for caffe, onnx, and other example models in the D-Robotics model conversion ``horizon_model_convert_sample`` example package: ``04_inference.sh`` and ``postprocess.py`` .
:::

```
# Load D-Robotics dependency libraries
