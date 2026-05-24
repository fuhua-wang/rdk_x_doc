  # Use nodes to specify non-quantized nodes for convenient usage
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

**API Usage**:

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

**Command-line Usage**:

```shell

  hmct-debugger plot_acc_error calibrated_model.onnx calibration_data -q ['weight','activation']
```

**Description**: quantize_node can also be set directly to 'weight' or 'activation'. When:

- quantize_node = ['weight']: Only quantize weights, do not quantize activations.

- quantize_node = ['activation']: Only quantize activations, do not quantize weights.

- quantize_node = ['weight', 'activation']: Quantize weights and activations separately.

![weight_activation_quantized](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/weight_activation_quantized.png)

- **plot_distribution**

**Functionality**: Select nodes and obtain the outputs of each node from the floating-point model and the calibrated model respectively to get the output data distribution. In addition, subtract the two outputs to obtain the error distribution between them.

**Command-line Format**:

```shell

  hmct-debugger plot-distribution MODEL_OR_FILE CALIBRATION_DATA --other options
```

Use ``hmct-debugger plot-distribution -h/--help`` to view related parameters.

**Parameter Group**:

| Parameter Name | Parameter Description | Value Range | Optional/Required |
|------------|----------|----------|--------|
|``save_dir or -s``| **Purpose**: Save path.<br/>**Description**: Optional. Specifies the save path for analysis results.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``model_or_file``| **Purpose**: Specify the calibrated model.<br/>**Description**: Required. Specifies the calibrated model to be analyzed.| **Value Range**: None.<br/> **Default**: None.|Required |
|``calibrated_data``| **Purpose**: Specify calibration data.<br/>**Description**: Required. Specifies the calibration data needed for analysis.| **Value Range**: None.<br/> **Default**: None.|Required |
|``nodes_list or -n``| **Purpose**: Specify nodes to be analyzed.<br/>**Description**: Required. Specifies the nodes to be analyzed.<br/>If the node type in nodes_list is:<br/>- Weight calibration node: Plot the data distribution of the original weights and the weights after calibration. <br/>- Activation calibration node: Plot the input data distribution of the activation calibration node.<br/>- Regular node: Plot the output data distribution of the node before and after quantization, and plot the error distribution between them.<br/>Note: nodes_list is of list type. You can specify a series of nodes, and the above three types of nodes can be specified at the same time.| **Value Range**: All nodes in the calibrated model.<br/> **Default**: None.|Required |

```shell

  # Import debug module
  import horizon_nn.debug as dbg

  dbg.plot_distribution(
          save_dir: str, 
          model_or_file: ModelProto or str,
          calibrated_data: str or CalibrationDataSet,
          nodes_list: List[str] or str) 
```

**Analysis Result Display**:

**API Usage**:

```shell

  # Import debug module
  import horizon_nn.debug as dbg

  dbg.plot_distribution(
          save_dir='./',
          model_or_file='./calibrated_model.onnx',
          calibrated_data='./calibration_data',
          nodes_list=['317_HzCalibration', # Activation node
                      '471_HzCalibration', # Weight node
                      'Conv_2']) # Regular node
```

**Command-line Usage**:

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

  In the three figures above, the blue triangle indicates the maximum absolute value of the data. The red dashed line indicates the minimum calibration threshold.
:::

- **get_channelwise_data_distribution**

**Functionality**: Plot box plots of the inter-channel data distribution of input data for specified calibration nodes.

**Command-line Format**:

```shell

  hmct-debugger get-channelwise-data-distribution MODEL_OR_FILE CALIBRATION_DATA --other options
```

Use ``hmct-debugger get-channelwise-data-distribution -h/--help`` to view related parameters.

**Parameter Group**:

| Parameter Name | Parameter Description | Value Range | Optional/Required |
|------------|----------|----------|--------|
|``save_dir or -s``| **Purpose**: Save path.<br/>**Description**: Optional. Specifies the save path for analysis results.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``model_or_file``| **Purpose**: Specify the calibrated model. <br/>**Description**: Required. Specifies the calibrated model to be analyzed.| **Value Range**: None.<br/> **Default**: None.|Required |
|``calibrated_data``| **Purpose**: Specify calibration data.<br/>**Description**: Required. Specifies the calibration data needed for analysis. | **Value Range**: None.<br/> **Default**: None.|Required |
|``nodes_list or -n``| **Purpose**: Specify calibration nodes.<br/>**Description**: Required. Specifies calibration nodes.| **Value Range**: All weight calibration nodes and activation calibration nodes in the calibrated model.<br/> **Default**: None.|Required |
|``axis or -a``| **Purpose**: Specify the dimension where channel is located.<br/>**Description**: The position of channel information in the shape. The parameter defaults to None. In this case, for activation calibration nodes, the second dimension of the node input data is considered to represent channel information by default, i.e., axis=1; for weight calibration nodes, the axis parameter in the node attributes is read as channel information. | **Value Range**: Less than the dimension of the node input data. <br/> **Default**: None.|Optional |

```shell

  # Import debug module
  import horizon_nn.debug as dbg

  dbg.get_channelwise_data_distribution(
          save_dir: str, 
          model_or_file: ModelProto or str,
          calibrated_data: str or CalibrationDataSet,
          nodes_list: List[str],
          axis: int = None)
```

**Analysis Result Display**:

**Description**: For the calibration node list node_list set by the user, obtain the dimension where channel is located from the axis parameter, and obtain the inter-channel data distribution of the node input data.
When axis defaults to None, if the node is a weight calibration node, the dimension where channel is located defaults to 0; if the node is an activation calibration node, the dimension where channel is located defaults to 1.

Weight calibration node:

![weight_calibration_node](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/weight_calibration_node.png)

Activation calibration node:

![activate_calibration_node](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/activate_calibration_node.png)

The output is shown below:

![box_plot](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/box_plot.png)

In the figure:

  - The horizontal axis represents the number of channels in the node input data. In the legend, the input data has 96 channels.

  - The vertical axis represents the data distribution range of each channel. The red solid line represents the median of the channel data, and the blue dashed line represents the mean.


- **runall**

:::caution Note

  In the current version, the runall feature is only applicable to **RDK Ultra and RDK X5** products.
:::

**Functionality**: Run all functions of the original debug tool with one click.

**Command-line Format**:

```shell

  hmct-debugger runall MODEL_OR_FILE CALIBRATION_DATA --other options
```

Use ``hmct-debugger runall -h/--help`` to view related parameters.
 
**Parameter Group**:

| Parameter Name | Parameter Description | Value Range | Optional/Required |
|------------|----------|----------|--------|
|``model_or_file``| **Purpose**: Specify the calibrated model.<br/>**Description**: Required. Specifies the calibrated model to be analyzed.| **Value Range**: None.<br/> **Default**: None.|Required |
|``calibrated_data``| **Purpose**: Specify calibration data.<br/>**Description**: Required. Specifies the calibration data needed for analysis.| **Value Range**: None.<br/> **Default**: None.|Required |
|``save_dir or -s``| **Purpose**: Save path.<br/>**Description**: Specifies the save path for analysis results.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``ns_metrics or -nm``| **Purpose**: Metric for node quantization sensitivity.<br/>**Description**: Specifies the calculation method for node quantization sensitivity. This parameter can be a list, meaning quantization sensitivity is calculated in multiple ways, but the output results are sorted only by the first method in the list. A higher ranking indicates that quantizing the node introduces greater error.| **Value Range**: ``'cosine-similarity'`` , ``'mse'`` , ``'mre'`` , ``'sqnr'`` , ``'chebyshev'`` .<br/> **Default**: ``'cosine-similarity'``.|Optional |
|``output_node or -o``| **Purpose**: Specify the output node.<br/>**Description**: This parameter allows you to specify an intermediate node as the output and calculate node quantization sensitivity. If the default parameter None is kept, the accuracy debug tool obtains the final output of the model and calculates node quantization sensitivity based on it.| **Value Range**: Regular nodes in the calibrated model that have corresponding calibration nodes.<br/> **Default**: None.|Optional |
|``node_type or -nt``| **Purpose**: Node type.<br/>**Description**: Node types for which quantization sensitivity needs to be calculated, including: node (regular node), weight (weight calibration node), activation (activation calibration node).| **Value Range**: ``'node'`` , ``'weight'`` , ``'activation'``.<br/> **Default**: ``'node'``.|Optional |
|``data_num or -dn``| **Purpose**: Number of data samples required to calculate quantization sensitivity.<br/>**Description**: Sets the number of data samples required when calculating node quantization sensitivity. Defaults to None, in which case all data in calibration_data is used for calculation. The minimum setting is 1, and the maximum is the number of data samples in calibration_data.| **Value Range**: Greater than 0 and less than or equal to the total number of data samples in calibration_data.<br/> **Default**: None.|Optional |
|``verbose or -v``| **Purpose**: Choose whether to print information to the terminal.<br/>**Description**: If True, quantization sensitivity information is printed to the terminal. If metrics contains multiple measurement methods, sorting is performed according to the first one.| **Value Range**: ``True`` , ``False``.<br/> **Default**: ``False``.|Optional |
|``interested_nodes or -i``| **Purpose**: Set nodes of interest.<br/>**Description**: If specified, only the quantization sensitivity of that node is obtained, and other nodes are not obtained. At the same time, if this parameter is specified, the node type specified by node_type is ignored, meaning this parameter has higher priority than node_type. If the default parameter None is kept, the quantization sensitivity of all quantizable nodes in the model is calculated.| **Value Range**: All nodes in the calibrated model.<br/> **Default**: None.|Optional |
|``dis_nodes_list or -dnl``| **Purpose**: Specify nodes to be analyzed.<br/>**Description**: Specify nodes to be analyzed.<br/>If the node type in nodes_list is: <br/>- Weight calibration node: Plot the data distribution of the original weights and the weights after calibration.<br/>- Activation calibration node: Plot the input data distribution of the activation calibration node.<br/>- Regular node: Plot the output data distribution of the node before and after quantization, and plot the error distribution between them. <br/>Note: nodes_list is of list type. You can specify a series of nodes, and the above three types of nodes can be specified at the same time.| **Value Range**: All nodes in the calibrated model.<br/> **Default**: None.|Optional |
|``cw_nodes_list or -cn``| **Purpose**: Specify calibration nodes.<br/>**Description**: Specify calibration nodes.| **Value Range**: All weight calibration nodes and activation calibration nodes in the calibrated model.<br/> **Default**: None.|Optional |
|``axis or -a``| **Purpose**: Specify the dimension where channel is located. <br/>**Description**: The position of channel information in the shape. The parameter defaults to None. In this case, for activation calibration nodes, the second dimension of the node input data is considered to represent channel information by default, i.e., axis=1; for weight calibration nodes, the axis parameter in the node attributes is read as channel information.| **Value Range**: Less than the dimension of the node input data.<br/> **Default**: None.|Optional |
|``quantize_node or -qn``| **Purpose**: Quantize only specified nodes in the model and view the error accumulation curve.<br/>**Description**: Optional parameter. Specifies nodes in the model that need to be quantized, while ensuring that all other nodes are not quantized.<br/>Determines whether it is single-node quantization or partial quantization by checking whether this parameter is a nested list.<br/>For example:<br/>- quantize_node=['Conv_2','Conv_9']: Quantize only Conv_2 and Conv_9 separately, while ensuring that other nodes are not quantized.<br/>- quantize_node=[['Conv_2'],['Conv_9','Conv_2']]: Quantize only Conv_2, and quantize Conv_2 and Conv_9 together, to test model cumulative error separately. <br/>- quantize_node contains two special parameters: 'weight' and 'activation'.<br/>When:<br/>- quantize_node = ['weight']: Only quantize weights, do not quantize activations.<br/>- quantize_node = ['activation']: Only quantize activations, do not quantize weights.<br/>- quantize_node = ['weight','activation']: Quantize weights and activations separately.<br/>Note: quantize_node and non_quantize_node cannot both be None; one of them must be specified.| **Value Range**: All nodes in the calibrated model.<br/> **Default**: None.|Optional |
|``non_quantize_node or -nqn``| **Purpose**: Specify the type of cumulative error.<br/>**Description**: Optional parameter. Specifies nodes in the model that are not quantized, while ensuring that all other nodes are quantized.<br/>Determines whether it is single-node non-quantization or partial non-quantization by checking whether this parameter is a nested list.<br/>For example:<br/>- non_quantize_node=['Conv_2','Conv_9']: Disable quantization for Conv_2 and Conv_9 separately, while ensuring that all other nodes are fully quantized.<br/>- non_quantize_node=[['Conv_2'],['Conv_9','Conv_2']]: Disable quantization for Conv_2 only, and disable quantization for Conv_2 and Conv_9 together, to test model cumulative error separately. <br/>Note: quantize_node and non_quantize_node cannot both be None; one of them must be specified.| **Value Range**: All nodes in the calibrated model.<br/> **Default**: None.|Optional |
|``ae_metric or -am``| **Purpose**: Cumulative error metric.<br/>**Description**: Sets the calculation method for model error.| **Value Range**: ``'cosine-similarity'`` , ``'mse'`` , ``'mre'`` , ``'sqnr'`` , ``'chebyshev'`` <br/> **Default**: ``'cosine-similarity'``.|Optional |
|``average_mode or -avm``| **Purpose**: Specify the output mode of the cumulative error curve.<br/>**Description**: Defaults to False. If True, the average of the cumulative error is obtained as the result.| **Value Range**: ``True`` , ``False``.<br/> **Default**: ``False``.|Optional |


**API Usage**:

```shell

  # Import debug module
  import horizon_nn.debug as dbg
  
  dbg.runall(model_or_file='calibrated_model.onnx',
             calibrated_data='calibration_data')
```

**Command-line Usage**:

```shell

  hmct-debugger runall calibrated_model.onnx calibration_data
```

runall workflow:

![runall](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/runall.png)

When all parameters remain at their defaults, the tool executes the following functions in sequence:

1. Obtain the quantization sensitivity of weight calibration nodes and activation calibration nodes separately.

2. Based on the results from step 1, take the top 5 weight calibration nodes and top 5 activation calibration nodes and plot their data distributions.

3. For the nodes obtained in step 2, plot box plots of their inter-channel data distributions separately.

4. Plot cumulative error curves for quantizing weights only and quantizing activations only separately.

When ``node_type='node'`` is specified, the tool obtains the top 5 nodes, finds the corresponding calibration node for each node, and obtains the data distribution and box plot of the calibration nodes.


Based on previous usage and tuning experience, the above strategies can already address various practical problems.

If the problem still cannot be resolved after the above attempts, please follow the steps in the [**Accuracy Tuning Checklist**](../../../08_FAQ/05_toolchain.md#checklist) document to fill in the specific model configuration information for inspection, ensure that each troubleshooting step has been completed, and use the checklist to identify the specific step in model conversion where the exception occurs. Then submit the completed **Accuracy Tuning Checklist** information, the original floating-point model file, model quantization-related configuration files, and other materials to the D-Robotics technical support team, or post your question in the [**D-Robotics Official Technical Community**](https://developer.d-robotics.cc/). We will provide support within 24 hours.


### Other Tool Usage Instructions

This section mainly introduces the usage of debug tools other than the model conversion tool. These tools can assist developers with model modification, model analysis, data preprocessing, and other operations. The tool list is as follows:

- hb_perf

- hb_pack

- hb_model_info

- hb_model_modifier

- hb_model_verifier

- hb_eval_preprocess


#### ``hb_perf`` Tool

``hb_perf`` is an analysis tool used to analyze the performance of D-Robotics quantized hybrid models.

- Usage

```
hb_perf [OPTIONS] BIN_FILE
```
- Command-line Parameters

Command-line parameters for hb_perf:

  --version<br/>
    Display version and exit.

  -m<br/>
    Followed by the model name. When BIN_FILE is specified as a pack model, only the model compilation information of the specified model is output.
    
  --help<br/>
    Display help information.

- Output Description

Model information is output to the `hb_perf_result` folder in the current directory.
There will be a folder named after the model, and the model information will be displayed in an `html` file named after the model. The directory structure is shown in the example below:

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

If the model was not set to debug mode during compilation (``compiler_parameters.debug:True``), the ``hb_perf`` tool will produce the following prompt.
This prompt only indicates that per-layer information is not included in the subgraph information and does not affect the generation of overall model information.
```
2021-01-12 10:41:40,000 WARNING bpu model don't have per-layer perf info.
2021-01-12 10:41:40,000 WARNING if you need per-layer perf info please enable[compiler_parameters.debug:True] when use makertbin.
```

#### ``hb_pack`` Tool

``hb_pack`` is a tool used to pack multiple hybrid model (\*.bin) files into a single model file.

- Usage

```
hb_pack [OPTIONS] BIN_FILE1 BIN_FILE2 BIN_FILE3 -o comb.bin
```

- Command-line Parameters

Command-line parameters for hb_pack:

  --version<br/>
    Display version and exit.

  -o, --output_name<br/>
    Output name of the pack model        

  --help<br/>
    Display help information.

- Output Description

The packed model is output to the current directory folder and is named according to the name specified by ``output_name``.
The compilation information and performance information of all sub-models in the packed model can be obtained through ``hb_model_info`` and ``hb_perf``.

:::caution Note
  Note that ``hb_pack`` does not support packing an already packed model again. Otherwise, the workbench will produce the following prompt:
:::
```bash
ERROR exception in command: pack
ERROR model: xxx.bin is a packed model, it can not be packed again!
```

#### ``hb_model_info`` Tool

``hb_model_info`` is a tool used to parse the dependencies and parameter information during the compilation of hybrid models (\*.bin).

- Usage

```bash
  hb_model_info ${model_file}
```
- Command-line Parameters

Command-line parameters for hb_model_info:

  --version<br/>
    Display version and exit.

  -m<br/>
    Followed by the model name. When BIN_FILE is specified as a pack model, only the model compilation information of the specified model is output.

  --help<br/>
    Display help information.

- Output Description

The output section contains some input information from model compilation, as shown below:

:::info Note
The version information in the code block below will change with the release package version. This is for reference only.
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

  When deleted nodes exist in the model, the names of the deleted nodes are printed at the end of the model information output, and a ``deleted_nodes_info.txt`` file is generated. Each line in the file records the initial information of the corresponding deleted node. The printed names of deleted nodes are shown below:
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

#### ``hb_model_modifier`` Tool

The ``hb_model_modifier`` tool is used to delete Transpose and Quantize nodes at the model input side, and Transpose, Dequanti, Cast, Reshape, and Softmax nodes at the model output side in ``*.bin`` models.
The information of deleted nodes is stored in the BIN model and can be viewed through ``hb_model_info``.

:::info Note
  1. The hb_model_modifier tool can only delete nodes that are directly adjacent to the model input or output. If the node to be deleted is followed by other nodes, it cannot be deleted.
  2. Model node names should not include special characters such as ";" and ",", otherwise tool usage may be affected.
  3. The tool does not support processing packed models. Otherwise, it will prompt: ``ERROR pack model is not supported``.
  4. Nodes to be deleted are removed sequentially in order, and the model structure is dynamically updated. Before deleting a node, the tool also checks whether the node is located at the model input or output. Therefore, the deletion order of nodes is important.
:::
Since deleting specific nodes affects the model input configuration, the tool is only applicable when there is only one path after the model input. As shown in the figure below, the case where the same input corresponds to multiple nodes is not yet supported.

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

3. Delete multiple specified nodes (using node1, node2, and node3 as examples):

```bash
  hb_model_modifier model.bin -r node1 -r node2 -r node3
```
4. Delete a type of node (using Dequantize as an example):

```bash
  hb_model_modifier model.bin --all Dequantize
```
5. Delete multiple types of nodes (using Reshape, Cast, and Dequantize as examples):

```bash
  hb_model_modifier model.bin -a Reshape -a Cast -a Dequantize
```
6. Combined usage:

```bash
  hb_model_modifier model.bin -a Reshape -a Cast -a Dequantize -r node1 -r node2 -r node3
```
- Command-line Parameters

Command-line parameters for hb_model_modifier:

  --model_file<br/>
    Runtime model file name.

  -r<br/>
    Followed by the name of the node to be deleted. If multiple nodes need to be deleted, this must be specified multiple times.

  -o<br/>
    Followed by the output name of the modified model (only effective when the ``-r`` parameter is present).

  -a --all<br/>
    Followed by the node type. Supports one-click deletion of all nodes of the corresponding type. If multiple types of nodes need to be deleted, this must be specified multiple times.

- Output Description

If the tool is run without any parameters, it prints the candidate deletable nodes (i.e., all Transpose, Quantize, Dequantize, Cast, Reshape, and Softmax nodes located at the input and output positions in the model).

Quantize nodes are used to quantize model float-type input data to int8 type. The calculation formula is as follows:

```bash
  qx = clamp(round(x / scale) + zero\_point, -128, 127)
```
``round(x)`` implements rounding of floating-point numbers. ``clamp(x)`` clamps the data to integer values between -128 and 127. ``zero_point`` is the zero-point offset value for asymmetric quantization. For symmetric quantization, ``zero_point = 0``.

The C++ reference implementation is as follows:
```cpp
  int64_t quantized_value =
      static_cast/<int64_t/>(std::round(value / static_cast/<double/(scale)));
  quantized_value = std::min(std::max(quantized_value, min_int_value), max_int_value);
```
Dequantize nodes are used to dequantize model ``int8`` or ``int32`` type output data back to ``float`` or ``double`` type. The calculation formula is as follows:

```bash
  deqx = (x - zero\_point) * scale
```
The C++ reference implementation is as follows:

```cpp
  static_cast/<float/>(value) * scale
```
:::info Note

  Currently, the tool supports deleting:

  1. Nodes at the input side that are Quantize or Transpose nodes;
  2. Nodes at the output side that are Transpose, Dequanti, Cast, Reshape, or Softmax nodes.
:::

The tool output is as follows:

```bash
hb_model_modifier resnet50_64x56x56_featuremap.bin
2022-04-21 18:22:30,207 INFO Nodes that can be deleted: ['data_res2a_branch1_HzQuantize_TransposeInput0', 'fc1000_reshape_0']
```
After specifying the ``-r`` option, the tool prints the node type in the model, the node information stored in the bin file, and indicates that the specified node has been deleted:

```bash
hb_model_modifier resnet50_64x56x56_featuremap.bin -r data_res2a_branch1_HzQuantize_TransposeInput0
Node 'data_res2a_branch1_HzQuantize_TransposeInput0' found, its OP type is 'Transpose'
Node 'data_res2a_branch1_HzQuantize_TransposeInput0' is removed
modified model saved as resnet50_64x56x56_featuremap_modified.bin
```
After that, you can use the ``hb_model_info`` tool to view deleted node information. The names of deleted nodes are printed at the end of the output information, and a ``deleted_nodes_info.txt`` file is generated. Each line in the file records the initial information of the corresponding deleted node. The printed names of deleted nodes are shown below:

```bash
hb_model_info resnet50_64x56x56_featuremap_modified.bin
Start hb_model_info....
hb_model_info version 1.7.0
********* resnet50_64x56x56_featuremap info *********
...
--------- deleted nodes -
deleted nodes: data_res2a_branch1_HzQuantize_TransposeInput0
```

#### ``hb_model_verifier`` Tool

The ``hb_model_verifier`` tool is used to verify results between a specified fixed-point model and a runtime model.
The tool uses a specified image to perform inference with the fixed-point model, runtime model on the board and x86 simulator, and runtime model inference on the board (if the given IP is reachable and ``hrt_tools`` is installed on the board; otherwise, you can use the ``install.sh`` script under ``package/board`` in the toolchain SDK package for installation), and runtime model inference on x86 (ensure ``hrt_tools`` is installed on the host;
otherwise, you can use the ``install.sh`` script under ``package/host`` in the toolchain SDK package for installation). It then performs pairwise comparison of the three results and provides a pass/fail conclusion. If no image is specified, the tool uses a default image for inference (for featuremap models, tensor data is randomly generated).

:::caution Note
  For how to obtain the ``package`` resource bundle, please refer to [**Deliverables Description**](../intermediate/environment_config.md#交付物使用说明).
:::
- Usage

```bash
  hb_model_verifier -q ${quanti_model} \
                    -b ${bin_model} \
                    -a ${board_ip} \
                    -i ${input_img} \
                    -d ${digits}
```
- Command-line Parameters

Command-line parameters for hb_model_verifier:

  -quanti_model, -q<br/>
    Fixed-point model name.

  --bin_model, -b<br/>
    bin model name.

  --arm-board-ip, -a<br/>
    ARM board IP address used for on-board testing.

  --input-img, -i<br/>
    Image used for inference testing. If not specified, a default image or random tensor is used. For image files in binary form, the file extension must be ``.bin``.

  --compare_digits, -d<br/>
    Compare inference result numerical precision. If not specified, five decimal places are compared by default.


- Output Description

The final comparison results are displayed in the terminal. The tool compares the ONNX model running results, simulator running results, and on-board results pairwise. If there are no issues, the output should be as follows:

```bash
  Quanti onnx and Arm result Strict check PASSED
```
When the fixed-point model and runtime model precision are inconsistent, specific information about the inconsistent results is output.

``mismatch line num`` is the number of results with inconsistent precision between the two models, including three types of inconsistency:

``mismatch.line_miss num`` is the number of cases where the number of output results is inconsistent;
``mismatch.line_diff num`` is the number of cases where the output result difference is too large;
``mismatch.line_nan num`` is the number of cases where the output is nan.

``total line num`` is the total number of output data entries.

``mismatch rate`` is the proportion of inconsistent data entries to the total number of output data entries.

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
  2. If the model has multiple outputs, only the first output result is compared.
  3. Verification of packed *.bin models is not currently supported. Otherwise, the workbench will produce the following prompt:
:::

```bash
  ERROR pack model is not supported
```

#### ``hb_eval_preprocess`` Tool{#hb_eval_preprocess}

Used to preprocess image data in an x86 environment when evaluating model accuracy.
Preprocessing refers to specific processing operations performed on image data before it is fed into the model.
For example: image resize, crop, and padding.

- Usage
```
  hb_eval_preprocess [OPTIONS]
```
- Command-line Parameters

Command-line parameters for hb_eval_preprocess:

  --version<br/>
    Display version and exit.

  -m, --model_name<br/>
    Set the model name. Supported model range can be viewed via ``hb_eval_preprocess --help``.

  -i, --image_dir<br/>
    Input image path.

  -o, --output_dir<br/>
    Output path.

  -v, --val_txt<br/>
    Set the file name of images required for evaluation. The preprocessed images will correspond to the image names in this file.

  -h, --help<br/>
    Display help information.

- Output Description

The ``hb_eval_preprocess`` command generates image binary files under the path specified by ``--output_dir``.

:::tip Tip
  For more application examples of the ``hb_eval_preprocess`` tool in on-board model accuracy evaluation, please refer to the
  [**Data Preprocessing**](./runtime_sample.md#数据预处理-1) section in the embedded application development document *Public Model Evaluation Instructions*.
:::
