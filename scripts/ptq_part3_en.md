from horizon_tc_ui import HB_ONNXRuntime

# Prepare feed_dict for model inference
def prepare_input_dict(input_names):
  feed_dict = dict()
  for input_name in input_names:
      # your_custom_data_prepare represents your custom data
      # Prepare data according to the input node type and layout requirements
      feed_dict[input_name] = your_custom_data_prepare(input_name)
  return feed_dict

if __name__ == '__main__':
  # Create inference Session
  sess = HB_ONNXRuntime(model_file='***_quantized_model.onnx')

  # Get input node names
  input_names = [input.name for input in sess.get_inputs()]
  # or
  input_names = sess.input_names

  # Get output node names
  output_names = [output.name for output in sess.get_outputs()]
  # or
  output_names = sess.output_names

  # Prepare model input data
  feed_dict = prepare_input_dict(input_names)
  # Start model inference; the return value is a list that corresponds one-to-one with output_names in order
  # Input image types: (RGB/BGR/NV12/YUV444/GRAY)
  outputs = sess.run(output_names, feed_dict, input_offset=128)
  # Input data types: (FEATURE)
  outputs = sess.run_feature(output_names, feed_dict, input_offset=0)

```

In the code above, the default value of the ``input_offset`` parameter is 128. For models with preprocessing nodes, a -128 operation is required here. If no preprocessing node is added before the model input, ``input_offset`` should be set to 0.

:::note Note
  For multi-input models:

  - If all input `input_type_rt` values belong to (RGB/BGR/NV12/YUV444/GRAY), you can use the `sess.run` method for inference.

  - If all input `input_type_rt` values belong to (FEATUREMAP), you can use the `sess.run_feature` method for inference.

  - Please note that mixed input types where some `input_type_rt` values are FEATUREMAP and others are not FEATUREMAP are currently not supported for inference using `sess.*` methods.
:::

In addition, the input data preparation process represented by the ``your_custom_data_prepare`` function is the part most prone to errors.
Compared with your original floating-point model design and training accuracy verification process, we recommend adjusting the inference input data after data preprocessing: mainly the data format (RGB, NV12, etc.), data precision (int8, float32, etc.), and data layout (NCHW or NHWC).
The adjustment method is jointly determined by the four parameters ``input_type_train``, ``input_layout_train``, ``input_type_rt``, and ``input_layout_rt`` set in the yaml configuration file during model conversion. For detailed rules, please refer to the [**Conversion Internal Process Interpretation**](#conversion_interpretation) section.

For example: an original floating-point model trained on ImageNet for classification has only one input node. This node accepts three-channel images in BGR order, with input data layout NCHW.
Then, during the original floating-point model design and training stage, the data preprocessing before validation set inference is as follows:

1. Scale the image proportionally, resizing the shorter side to 256.
2. Use the ``center_crop`` method to obtain a 224x224 image.
3. Subtract mean per channel.
4. Multiply data by the scale coefficient.

When D-Robotics converts this original floating-point model,
``input_type_train`` is set to ``bgr``, ``input_layout_train`` is set to ``NCHW``, ``input_type_rt`` is set to ``bgr``,
and ``input_layout_rt`` is set to ``NHWC``.
According to the rules introduced in the [**Conversion Internal Process Interpretation**](#conversion_interpretation) section, the input accepted by ***_quantized_model.onnx should be bgr_128 with NHWC layout.
Corresponding to the sample code above, the data processing provided by the ``your_custom_data_prepare`` section is as follows:

```
# This example uses skimage; if using opencv there will be differences
# Please note that subtract-mean and multiply-scale processing is not shown in transformers
# mean and scale operations have been fused into the model; refer to norm_type/mean_value/scale_value configuration above
def your_custom_data_prepare_sample(image_file):
  # skimage reads images, already in NHWC layout
  image = skimage.img_as_float(skimage.io.imread(image_file))
  # Proportional scale, resize shorter side to 256
  image = ShortSideResize(image, short_size=256)
  # CenterCrop to obtain 224x224 image
  image = CenterCrop(image, crop_size=224)
  # skimage read result channel order is RGB; convert to BGR order required by bgr_128
  image = RGB2BGR(image)
  # If the original model is NCHW input (except when input_type_rt is nv12)
  if layout == "NCHW":
    image = HWC2CHW(image)
  # skimage read value range is [0.0, 1.0]; adjust to value range required by bgr
  image = image * 255
  # bgr_128 is bgr minus 128
  image = image - 128
  # bgr_128 uses int8
  image = image.astype(np.int8)
  
  return image
```


#### Accuracy Tuning

Based on the accuracy analysis work above, if you determine that the model's quantization accuracy does not meet expectations, the main solutions can be divided into the following situations:

- 1. Significant accuracy loss (loss greater than 4%).
  This type of problem is often caused by improper yaml configuration, imbalanced calibration datasets, etc. We recommend troubleshooting one by one according to the suggestions provided by D-Robotics below.

- 2. Minor accuracy loss (1.5%~3%).
  After ruling out accuracy issues caused by item 1, if there is still a small accuracy loss, it is often due to the model's own sensitivity. We recommend using the accuracy tuning tools provided by D-Robotics.

- 3. After trying items 1 and 2, if accuracy still cannot meet expectations, you can try using our accuracy debug tools for further attempts.

The overall accuracy problem resolution flow is illustrated below:

![accuracy_problem](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/accuracy_problem.png)

##### Significant Accuracy Loss (Above 4%)


If model accuracy loss is greater than 4%, it is usually caused by improper yaml configuration, imbalanced calibration datasets, etc. We recommend troubleshooting sequentially from pipeline, model conversion configuration, and consistency checks.

**Pipeline Check**

Pipeline refers to the entire process of data preprocessing, model conversion, model inference, post-processing, and accuracy evaluation. Please check these steps according to the corresponding sections above.
From past practical problem follow-up experience, we found that in most cases, changes were made during the original floating-point model training stage but were not updated in time to the model conversion step, causing anomalies during accuracy verification.

**Model Conversion Configuration Check**

- ``input_type_rt`` and ``input_type_train`` are used to distinguish the data formats required by the converted hybrid heterogeneous model and the original floating-point model. Check carefully whether they meet expectations, especially whether the BGR and RGB channel order is correct.

- Whether parameters such as ``norm_type``, ``mean_value``, and ``scale_value`` are configured correctly. Through conversion configuration, mean and scale operation nodes can be inserted directly into the model. Confirm whether duplicate mean and scale operations were performed on calibration/test images. **Duplicate preprocessing is a common error-prone area**.

**Data Processing Consistency Check**

This check mainly targets users who prepare calibration data and evaluation code based on the reference algorithm toolchain development package examples. Common errors include:

- ``read_mode`` not specified correctly: In 02_preprocess.sh, you can specify the image reading method via the --read_mode parameter, supporting ``opencv`` and ``skimage``.
  In addition, preprocess.py also sets the image reading method via the imread_mode parameter, which also needs to be modified. Using skimage for image reading yields ``RGB`` channel order, value range ``0~1``, and numeric type ``float``; while using opencv yields ``BGR`` channel order, value range ``0~255``, and data type ``uint8``.

- Incorrect calibration dataset storage format: D-Robotics currently uses ``numpy.tofile`` to save calibration data. This method does not save shape and type information. If input_type_train is in ``non-featuremap`` format, the data dtype is determined by whether the calibration data storage path contains "f32". If it contains the f32 keyword, data is parsed as float32; otherwise it is parsed as uint8.
  In addition, to facilitate users in setting calibration data parsing methods, after algorithm toolchain v2.2.3a, a new parameter ``cal_data_type`` was added to the yaml to set the data storage type of binary files.

- Inconsistent transformer implementation: D-Robotics provides a series of common preprocessing functions stored in the ``/horizon_model_convert_sample/01_common/python/data/transformer.py`` file. The implementation of some preprocessing operations may differ. For example, ResizeTransformer uses opencv's default interpolation method (linear).
  If other interpolation methods are needed, you can directly modify the transformer.py source code to ensure consistency with the preprocessing code during training. For specific usage, please refer to the [**transformer Usage**](../../../08_FAQ/05_toolchain.md#transposetransformer) section.

- We recommend that during D-Robotics algorithm toolchain usage, you continue to use the data processing libraries relied upon during the original floating-point model training and verification stage.
  For models with poor robustness, typical functions such as resize and crop implemented by different libraries may cause perturbations, thereby affecting model accuracy.

- Whether the calibration image set is reasonably configured. The calibration image set quantity should be around ``one hundred``, and it is best to cover various scenarios in the data distribution. For example, in multi-task or multi-classification scenarios, the calibration image set can cover each prediction branch or each category.
  Also avoid abnormal images that deviate from the data distribution (over-exposure, etc.).

- Use ``***_original_float_model.onnx`` to verify accuracy again. Under normal circumstances, this model's accuracy should align with the original floating-point model accuracy to ``three to five decimal places``.
  If verification shows this alignment is not met, your data processing needs to be checked more carefully.

##### Improving Minor Accuracy Loss

In general, to reduce the difficulty of model accuracy tuning, we recommend first trying to configure ``calibration_type`` as ``default``. default is an automatic search function that selects the optimal scheme from max, max-Percentile 0.99995, KL, and other calibration methods based on the cosine similarity of the first calibration data output node.
The finally selected calibration method can be found in conversion logs with prompts similar to ``"Select kl method."``. If the automatic search accuracy result still differs from expectations, you can try the following suggestions for tuning:

**Adjust Calibration Method**

- Manually specify calibration_type; you can choose ``kl/max``;

- Configure calibration_type as max and configure max_percentile to different quantiles (value range is 0-1). We recommend first trying 0.99999, 0.99995, 0.9999, 0.9995, and 0.999. Observe the model accuracy change trend through these five configurations and finally find the optimal quantile;
  
- Try enabling ``per_channel``; it can be used together with any previous calibration method.

**Tune Calibration Dataset**

- You can try appropriately ``increasing or decreasing`` the data quantity (generally detection scenarios require less calibration data than classification scenarios; additionally, observe missed detections in model output and appropriately increase calibration data for corresponding scenarios);

- Do not use abnormal data such as pure black or pure white images. Minimize using background images without targets as calibration data. Cover typical task scenarios as comprehensively as possible so that the calibration dataset distribution approximates the training set.

**Revert Some Tail Operators to CPU High-Precision Computation**

- Generally we only try reverting ``1~2`` operators in the model output layer to ``CPU``. Too many operators will significantly affect final model performance. The judgment basis can be obtained by observing the model's ``cosine similarity``;

- To specify operators running on CPU, use the ``run_on_cpu`` parameter in the yaml file. Specify node names to run corresponding operators on CPU (example: run_on_cpu: conv_0).

- If the model compilation reports an error after run_on_cpu, please contact the D-Robotics technical support team.


##### Accuracy Debug Tools

After trying the two accuracy tuning methods above, if your accuracy still cannot meet expectations, to help you locate problems, we provide accuracy debug tools to assist in problem localization.
These tools can help you perform node-level quantization error analysis on the calibrated model and quickly locate nodes with accuracy anomalies.

:::tip Tip

  If you are using **RDK Ultra and RDK X5** products, you can also try accuracy tuning by configuring some ops to compute in int16 (**RDK X3** does not support int16 operator computation):

  During model conversion, most ops compute with int8 data by default. In some scenarios, int8 computation for some ops causes significant accuracy loss.
  For **RDK Ultra and RDK X5** products, the algorithm toolchain currently provides the ability to specify certain ops to compute in int16 bit.
  For details, refer to the [**int16 Configuration**](#int16_config) parameter configuration description.
  By configuring quantization accuracy loss-sensitive ops (using cosine similarity as reference) to compute in int16 bit, accuracy loss problems can be resolved in some scenarios.
:::

During model conversion, accuracy loss is inevitably introduced due to the floating-point to fixed-point quantization process. The main causes of accuracy loss are usually the following:

1. Some nodes in the model are sensitive to quantization and introduce significant errors, i.e., sensitive node quantization problems.

2. Error accumulation across nodes in the model causes significant overall calibration error in the model, mainly including: error accumulation from weight quantization, error accumulation from activation quantization, and error accumulation from full quantization.

For this situation, D-Robotics provides accuracy debug tools to help you independently locate accuracy problems generated during model quantization.
These tools can help you perform node-level quantization error analysis on the calibrated model and ultimately help you quickly locate nodes with accuracy anomalies.

The accuracy debug tools provide various analysis functions for your use, such as:

- Obtain node quantization sensitivity.

- Obtain model cumulative error curves.

- Obtain data distribution of specified nodes.

- Obtain box plots of inter-channel data distribution for specified node input data, etc.

###### Usage Instructions

Using the accuracy debug tools mainly involves the following steps:

1. Configure parameter ``debug_mode="dump_calibration_data"`` in the **Model Parameters (model_parameters)** group in yaml to save calibration data.

2. Import the debug module and load the calibrated model and data.

3. Analyze models with significant accuracy loss through the APIs or command line provided by the accuracy debug tools.

:::note Note

  For the current version of the accuracy debug tools: **RDK Ultra** corresponding ``bayes`` architecture models support command-line and API methods, **RDK X5** corresponding ``bayes-e`` architecture models support command-line and API methods, and **RDK X3** corresponding ``bernoulli2`` architecture models only support API method for debug.
:::

The overall flow is shown in the figure below:

![accuracy_debug_process](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/accuracy_debug_process.png)

- **Saving Calibrated Model and Data**

First, you need to configure ``debug_mode="dump_calibration_data"`` in the yaml file to enable the accuracy debug function,
and save calibration data (calibration_data). The corresponding calibrated model (calibrated_model.onnx) is saved by default. Among them:

1. Calibration data (calibration_data): During the calibration stage, the model performs forward inference on this data to obtain quantization parameters for each quantized node, including: scale factor (scale) and threshold.

2. Calibrated model (calibrated_model.onnx): Saves the quantization parameters calculated for each quantized node during the calibration stage in calibration nodes, thereby obtaining the calibrated model.

:::note Note

  **What is the difference between calibration data saved here and calibration data generated by 02_preprocess.sh?**

  Calibration data obtained from ``02_preprocess.sh`` is in BGR color space. Inside the toolchain, data is converted from BGR to the actual model input format such as yuv444/gray.
  Calibration data saved here is in .npy format after color space conversion and preprocessing. This data can be loaded with np.load() and fed directly into the model for inference.
:::

:::note Note

  **Calibrated Model (calibrated_model.onnx) Interpretation**

  The calibrated model is an intermediate product obtained after the model conversion toolchain optimizes the floating-point model structure, calculates quantization parameters for each node through calibration data, and saves them in calibration nodes.
  The main characteristic of the calibrated model is that it contains calibration nodes. The node type of calibration nodes is HzCalibration.
  These calibration nodes are mainly divided into two categories: **activation calibration nodes** and **weight calibration nodes**.

  The input of **activation calibration nodes** is the output of the previous node of the current node. Based on the quantization parameters (scales and thresholds) saved in the current activation calibration node, the input data is quantized and dequantized before output.

  The input of **weight calibration nodes** is the original floating-point weights of the model. Based on the quantization parameters (scales and thresholds) saved in the current weight calibration node, the original floating-point weights are quantized and dequantized before output.

  Aside from the calibration nodes above, other nodes in the calibrated model are called **regular nodes (node)** by the accuracy debug tools.
  **Regular nodes** include types such as: Conv, Mul, Add, etc.
:::

![debug_node](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/debug_node.png)

The folder structure of calibration_data is as follows:

```shell

  |--calibration_data : calibration data
  |----input.1 : folder name is the model input node and saves corresponding input data
  |--------0.npy
  |--------1.npy
  |-------- ...
  |----input.2 : for multi-input models, multiple folders will be saved
  |--------0.npy
  |--------1.npy
  |-------- ...
```

- **Accuracy Debug Module Import and Usage**

Next, you need to import the debug module in code and obtain node quantization sensitivity through the ``get_sensitivity_of_nodes`` interface (cosine similarity of model output is used by default).
For detailed parameter description of ``get_sensitivity_of_nodes``, see the ``get_sensitivity_of_nodes`` section.

```shell

  # Import debug module
  import horizon_nn.debug as dbg
  # Import log module
  import logging

  # When verbose=True, set log level to INFO first
  logging.getLogger().setLevel(logging.INFO)
  # Obtain node quantization sensitivity
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

- **Analysis Result Display**

The print result when ``verbose=True`` is shown below:

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

In addition, this API returns node quantization sensitivity information to you in dictionary (Dict) format for subsequent analysis.

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

For more functions, please refer to the **Function Description** section.

:::tip Tip

  The accuracy debug tools can also use the command line ``hmct-debugger -h/--help`` to view subcommands corresponding to each function.
  Detailed parameters and usage of each subcommand are described in the **Function Description** section.
:::

###### Function Description

- **get_sensitivity_of_nodes**

**Functionality**: Obtain node quantization sensitivity.

**Command-line Format**:

```shell

  hmct-debugger get-sensitivity-of-nodes MODEL_OR_FILE CALIBRATION_DATA --other options
```

Use ``hmct-debugger get-sensitivity-of-nodes -h/--help`` to view related parameters.

**Parameter Group**:

| Parameter Name | Parameter Description | Value Range | Optional/Required |
|------------|----------|----------|--------|
|``model_or_file``| **Purpose**: Specify the calibrated model.<br/>**Description**: Required. Specifies the calibrated model to be analyzed.| **Value Range**: None.<br/> **Default**: None.|Required |
|``metrics or - m``| **Purpose**: Metric for node quantization sensitivity.<br/>**Description**: Specifies the calculation method for node quantization sensitivity. This parameter can be a list, i.e., calculate quantization sensitivity in multiple ways, but the output results are sorted only by the first method in the list. Higher ranking indicates greater error introduced by quantizing that node.| **Value Range**: ``'cosine-similarity'`` , ``'mse'`` , ``'mre'`` , ``'sqnr'`` , ``'chebyshev'``.<br/> **Default**: ``'cosine-similarity'``.|Optional |
|``calibrated_data``| **Purpose**: Specify calibration data.<br/>**Description**: Required. Specifies the calibration data needed for analysis.| **Value Range**: None.<br/> **Default**: None.|Required |
|``output_node or -o``| **Purpose**: Specify output node.<br/>**Description**: This parameter supports specifying intermediate nodes as output and calculating node quantization sensitivity. If the default parameter None is kept, the accuracy debug tool obtains the final output of the model and calculates node quantization sensitivity based on it.| **Value Range**: Regular nodes in the calibrated model that have corresponding calibration nodes.<br/> **Default**: None.|Optional |
|``node_type or -n``| **Purpose**: Node type.<br/>**Description**: Node type for which quantization sensitivity needs to be calculated, including: node (regular node), weight (weight calibration node), activation (activation calibration node).| **Value Range**: ``'node'`` , ``'weight'`` , ``'activation'``.<br/> **Default**: ``'node'``.|Optional |
|``data_num or -d``| **Purpose**: Number of data samples needed to calculate quantization sensitivity.<br/>**Description**: Sets the number of data samples needed when calculating node quantization sensitivity. Default is None, in which case all data in calibration_data is used. Minimum is 1, maximum is the total number of data in calibration_data.| **Value Range**: Greater than 0, less than or equal to the total number of data in calibration_data.<br/> **Default**: None|Optional |
|``verbose or -v``| **Purpose**: Choose whether to print information to the terminal.<br/>**Description**: If True, quantization sensitivity information is printed to the terminal. If metrics contains multiple measurement methods, sorting is based on the first one.| **Value Range**: ``True`` , ``False``.<br/> **Default**: ``False``.|Optional |
|``interested_nodes or -i``| **Purpose**: Set nodes of interest.<br/>**Description**: If specified, only the quantization sensitivity of that node is obtained; other nodes are not obtained. Also, if this parameter is specified, the node type specified by node_type is ignored, meaning this parameter has higher priority than node_type. If the default parameter None is kept, quantization sensitivity is calculated for all quantizable nodes in the model.| **Value Range**: All nodes in the calibrated model.<br/> **Default**: None.|Optional |

Function usage:

```shell

  # Import debug module
  import horizon_nn.debug as dbg
  # Import log module
  import logging

  # When verbose=True, set log level to INFO first
  logging.getLogger().setLevel(logging.INFO)
  # Obtain node quantization sensitivity
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

Command-line usage:

```shell

  hmct-debugger get-sensitivity-of-nodes calibrated_model.onnx calibration_data -m ['cosine-similarity','mse'] -v True
```

**Analysis Result Display**:

**Description**: First set the node type for which sensitivity needs to be calculated via node_type. Then the tool obtains all nodes in the calibrated model that match node_type and obtains their quantization sensitivity.
When verbose is set to True, the tool sorts and prints node quantization sensitivity to the terminal. Higher ranking indicates greater quantization error introduced by quantizing that node.

Print result when verbose=True:

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

Function return value:

  The function return value is quantization sensitivity saved in dictionary format (Key is node name, Value is node quantization sensitivity information), in the following format:

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

**Functionality**: Quantize only one node in the floating-point model, and sequentially calculate the error between that model and the floating-point model node outputs to obtain cumulative error curves.

**Command-line Format**:

```shell

  hmct-debugger plot-acc-error MODEL_OR_FILE CALIBRATION_DATA --other options
```

Use ``hmct-debugger plot-acc-error -h/--help`` to view related parameters.

**Parameter Group**:

| Parameter Name | Parameter Description | Value Range | Optional/Required |
|------------|----------|----------|--------|
|``save_dir or -s``| **Purpose**: Save path.<br/>**Description**: Optional. Specifies the save path for analysis results.| **Value Range**: None.<br/> **Default**: None.|Optional |
|``calibrated_data``| **Purpose**: Specify calibration data.<br/>**Description**: Required. Specifies the calibration data to be analyzed.| **Value Range**: None.<br/> **Default**: None.|Required |
|``model_or_file``| **Purpose**: Specify the calibrated model.<br/>**Description**: Required. Specifies the calibrated model to be analyzed.| **Value Range**: None.<br/> **Default**: None.|Required |
|``quantize_node or -q``| **Purpose**: Quantize only specified nodes in the model and view error accumulation curves.<br/>**Description**: Optional parameter. Specifies nodes in the model that need to be quantized while ensuring all other nodes are not quantized.<br/>Determines single-node quantization or partial quantization by checking whether this parameter is a nested list.<br/>For example:<br/>- quantize_node=['Conv_2','Conv_9']: Quantize Conv_2 and Conv_9 separately while ensuring other nodes are not quantized.<br/>- quantize_node=[['Conv_2'],['Conv_9','Conv_2']]: Quantize only Conv_2 and quantize Conv_2 and Conv_9 simultaneously, respectively testing model cumulative error.<br/>- quantize_node contains two special parameters: 'weight' and 'activation'.<br/>When:<br/>- quantize_node = ['weight']: Quantize weights only, do not quantize activations.<br/>- quantize_node = ['activation']: Quantize activations only, do not quantize weights.<br/>- quantize_node = ['weight','activation']: Quantize weights and activations separately.<br/>Note: quantize_node and non_quantize_node cannot both be None; one must be specified.| **Value Range**: All nodes in the calibrated model.<br/> **Default**: None.|Optional |
|``non_quantize_node or -nq``| **Purpose**: Specify cumulative error type.<br/>**Description**: Optional parameter. Specifies nodes in the model that are not quantized while ensuring all other nodes are quantized.<br/>Determines single-node non-quantization or partial non-quantization by checking whether this parameter is a nested list.<br/>For example:<br/>- non_quantize_node=['Conv_2','Conv_9']: De-quantize Conv_2 and Conv_9 separately while ensuring all other nodes are fully quantized.<br/>- non_quantize_node=[['Conv_2'],['Conv_9','Conv_2']]: De-quantize only Conv_2 and de-quantize Conv_2 and Conv_9 simultaneously, respectively testing model cumulative error.<br/>Note: quantize_node and non_quantize_node cannot both be None; one must be specified.| **Value Range**: All nodes in the calibrated model.<br/> **Default**: None.|Optional |
|``metric or -m``| **Purpose**: Error metric.<br/>**Description**: Sets the calculation method for model error.| **Value Range**: ``'cosine-similarity'`` , ``'mse'`` , ``'mre'`` , ``'sqnr'`` , ``'chebyshev'``<br/> **Default**: ``'cosine-similarity'``.|Optional |
|``average_mode or -a``| **Purpose**: Specify cumulative error curve output mode.<br/>**Description**: Default is False. If True, the average of cumulative errors is obtained as the result.| **Value Range**: ``True`` , ``False``.<br/> **Default**: ``False``.|Optional |

```shell

  # Import debug module
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

**Analysis Result Display**

**1. Specified Node Quantization Cumulative Error Test**

- Specify single node quantization

**Configuration**: quantize_node=['Conv_2', 'Conv_90'], quantize_node is a single list.

API function usage:

```shell

  # Import debug module
  import horizon_nn.debug as dbg

  dbg.plot_acc_error(
          save_dir='./',
          calibrated_data='./calibration_data/',
          model_or_file='./calibrated_model.onnx',
          quantize_node=['Conv_2', 'Conv_90'],
          metric='cosine-similarity',
          average_mode=False)
```

Command-line usage:

```shell

  hmct-debugger plot-acc-error calibrated_model.onnx calibration_data -q ['Conv_2','Conv_90']
```

**Description**: When quantize_node is a single list, for the quantize_node you set,
each node in quantize_node is quantized separately while other nodes in the model are kept unquantized. After obtaining the corresponding model,
the error between each node's output in that model and the corresponding node output in the floating-point model is calculated, and the corresponding cumulative error curve is obtained.

When average_mode = False:

![average_mode_false_1](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/average_mode_false_1.png)

When average_mode = True:

![average_mode_true_1](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/average_mode_true_1.png)

:::note Note

  **average_mode**

  average_mode defaults to False. For some models, the cumulative error curve cannot be used to determine which quantization strategy is more effective at this time.
  Therefore, average_mode needs to be set to True. At this time, the average of cumulative errors of the first n nodes is used as the cumulative error of the nth node.

  The specific calculation method is as follows, for example:

  When average_mode=False, accumulate_error=[1.0, 0.9, 0.9, 0.8].

  When average_mode=True, accumulate_error=[1.0, 0.95, 0.933, 0.9].
:::

- Specify multiple node quantization

**Configuration**: quantize_node=[['Conv_2'], ['Conv_2', 'Conv_90']], quantize_node is a nested list

API usage:

```shell

  # Import debug module
  import horizon_nn.debug as dbg

  dbg.plot_acc_error(
          save_dir='./',
          calibrated_data='./calibration_data/',
          model_or_file='./calibrated_model.onnx',
          quantize_node=[['Conv_2'], ['Conv_2', 'Conv_90']],
          metric='cosine-similarity',
          average_mode=False)
```

Command-line usage:

```shell

  hmct-debugger plot-acc-error calibrated_model.onnx calibration_data -q [['Conv_2'],['Conv_2','Conv_90']]
```

**Description**: When quantize_node is a nested list, for the quantize_node you set, each single list specified in quantize_node is quantized separately
while other nodes in the model are kept unquantized. After obtaining the corresponding model, the error between each node's output
and the corresponding node output in the floating-point model is calculated, and the corresponding cumulative error curve is obtained.

- partial_qmodel_0: Quantize only Conv_2 node, other nodes not quantized;

- partial_qmodel_1: Quantize only Conv_2 and Conv_90 nodes, other nodes not quantized.

When average_mode=False:

![new_average_mode_false_1](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/new_average_mode_false_1.png)

When average_mode=True:

![new_average_mode_true_1](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/new_average_mode_true_1.png)

**2. Cumulative Error Test After De-quantizing Partial Model Nodes**

- Specify single node non-quantization

**Configuration**: non_quantize_node=['Conv_2', 'Conv_90'], non_quantize_node is a single list.

API usage:

```shell

  # Import debug module
  import horizon_nn.debug as dbg

  dbg.plot_acc_error(
          save_dir='./',
          calibrated_data='./calibration_data/',
          model_or_file='./calibrated_model.onnx',
          non_quantize_node=['Conv_2', 'Conv_90'],
          metric='cosine-similarity',
          average_mode=True)
```

Command-line usage:

```shell

  hmct-debugger plot-acc-error calibrated_model.onnx calibration_data -nq ['Conv_2','Conv_90'] -a True
```

**Description**: When non_quantize_node is a single list, for the non_quantize_node you set,
quantization of each node in non_quantize_node is removed separately while all other nodes remain fully quantized. After obtaining the corresponding model,
the error between each node's output and the corresponding node output in the floating-point model is calculated, and the corresponding cumulative error curve is obtained.

When average_mode = False:

![average_mode_false_2](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/average_mode_false_2.png)

When average_mode = True:

![average_mode_true_2](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/average_mode_true_2.png)

- Specify multiple node non-quantization

**Configuration**: non_quantize_node=[['Conv_2'], ['Conv_2', 'Conv_90']], non_quantize_node is a nested list.

API usage:

```shell

  # Import debug module
  import horizon_nn.debug as dbg

  dbg.plot_acc_error(
          save_dir='./',
          calibrated_data='./calibration_data/',
          model_or_file='./calibrated_model.onnx',
          non_quantize_node=[['Conv_2'], ['Conv_2', 'Conv_90']],
          metric='cosine-similarity',
          average_mode=False)
```

Command-line usage:

```shell

  hmct-debugger plot-acc-error calibrated_model.onnx calibration_data -nq [['Conv_2'],['Conv_2','Conv_90']]
```

**Description**: When non_quantize_node is a nested list, for the non_quantize_node you set,
each single list specified in non_quantize_node is kept unquantized while all other nodes in the model are quantized.
After obtaining the corresponding model, the error between each node's output and the corresponding node output in the floating-point model is calculated,
and the corresponding cumulative error curve is obtained.

- partial_qmodel_0: Do not quantize Conv_2 node, quantize all other nodes;

- partial_qmodel_1: Do not quantize Conv_2 and Conv_90 nodes, quantize all other nodes.

When average_mode = False:

![new_average_mode_false_2](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/new_average_mode_false_2.png)

When average_mode = True:

![new_average_mode_true_2](https://rdk-doc.oss-cn-beijing.aliyuncs.com/doc/img/07_Advanced_development/04_toolchain_development/intermediate/new_average_mode_true_2.png)

**Testing Tips**:

When testing partial quantization accuracy, you may compare accuracy across multiple quantization strategies sorted by quantization sensitivity. In this case, you can refer to the following usage:

```shell

  # Import debug module
  import horizon_nn.debug as dbg

  # First use the quantization sensitivity sorting function to obtain node quantization sensitivity ranking in the model
  node_message = dbg.get_sensitivity_of_nodes(
          model_or_file='./calibrated_model.onnx',
          metrics='cosine-similarity',
          calibrated_data='./calibration_data/',
          output_node=None,
          node_type='node',
          verbose=False,
          interested_nodes=None)
        
  # node_message is a dictionary type with node names as keys
  nodes = list(node_message.keys())
