#!/usr/bin/env python3
"""Generate English translation of ptq_process.md from Chinese source."""
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "docs/07_Advanced_development/04_toolchain_development/intermediate/ptq_process.md"
DST = ROOT / "i18n/en/docusaurus-plugin-content-docs/current/07_Advanced_development/04_toolchain_development/intermediate/ptq_process.md"

text = SRC.read_text(encoding="utf-8")

# --- Section-level full translations (Chinese -> English) ---
# Order matters: longer/more specific strings first.

SECTION_TRANSLATIONS = [
    # Title & intro
    ("# PTQ原理及步骤详解", "# PTQ Principles and Step-by-Step Guide"),
    ("### 简介{#PTQ_introduction}", "### Introduction{#PTQ_introduction}"),
    (
        "模型转换是指将原始浮点模型转换为D-Robotics 混合异构模型的过程。原始浮点模型（文中部分地方也称为浮点模型）是指您通过TensorFlow/PyTorch等DL框架训练得到的可用模型，这个模型的计算精度为float32；混合异构模型是一种适合在D-Robotics 处理器上运行的模型格式。\n本章节将反复使用到这两种模型名词，为避免理解歧义，请先理解这个概念再阅读下文。",
        "Model conversion refers to the process of converting an original floating-point model into a D-Robotics hybrid heterogeneous model. The original floating-point model (also referred to as a floating-point model in some places in this document) is a usable model you obtain by training with DL frameworks such as TensorFlow/PyTorch, with float32 computation precision. A hybrid heterogeneous model is a model format suitable for running on D-Robotics processors.\nThis chapter will repeatedly use these two model terms. To avoid ambiguity, please understand these concepts before reading further.",
    ),
    (
        "配合D-Robotics 算法工具链的模型完整开发过程，需要经过 **浮点模型准备**、 **模型验证**、 **模型转换**、 **性能评估** 和 **精度评估** 共五个重要阶段，如下图:",
        "The complete model development process with the D-Robotics algorithm toolchain requires five important stages: **Floating-Point Model Preparation**, **Model Verification**, **Model Conversion**, **Performance Evaluation**, and **Accuracy Evaluation**, as shown below:",
    ),
    (
        "**浮点模型准备** 本阶段用来确保原始浮点模型的格式为D-Robotics 模型转换工具支持的格式，原始浮点模型来自于您通过TensorFlow/PyTorch等DL框架训练得到可用模型。具体的浮点模型要求与建议，请阅读[**浮点模型准备**](#model_preparation)章节内容。",
        "**Floating-Point Model Preparation** This stage ensures that the original floating-point model format is supported by the D-Robotics model conversion tool. The original floating-point model comes from a usable model you train with DL frameworks such as TensorFlow/PyTorch. For specific floating-point model requirements and recommendations, please read the [**Floating-Point Model Preparation**](#model_preparation) section.",
    ),
    (
        "**模型验证** 本阶段用来校验原始浮点模型是否满足D-Robotics 算法工具链的要求。D-Robotics 提供 ``hb_mapper checker`` 检查工具来完成浮点模型的检查。具体使用方法，请阅读[**验证模型**](#model_check) 章节内容。",
        "**Model Verification** This stage verifies whether the original floating-point model meets the requirements of the D-Robotics algorithm toolchain. D-Robotics provides the ``hb_mapper checker`` tool to check floating-point models. For detailed usage, please read the [**Model Verification**](#model_check) section.",
    ),
    (
        "**模型转换** 本阶段用来完成浮点模型到D-Robotics 混合异构模型的转换，经过这个阶段，您将得到一个可以在D-Robotics 处理器上运行的模型。D-Robotics 提供 ``hb_mapper makertbin`` 转换工具来完成模型优化、量化和编译等关键步骤。具体使用方法，请阅读[**模型转换**](#model_conversion)章节内容。",
        "**Model Conversion** This stage completes the conversion from a floating-point model to a D-Robotics hybrid heterogeneous model. After this stage, you will obtain a model that can run on D-Robotics processors. D-Robotics provides the ``hb_mapper makertbin`` conversion tool to complete key steps such as model optimization, quantization, and compilation. For detailed usage, please read the [**Model Conversion**](#model_conversion) section.",
    ),
    (
        "**性能评估** 本阶段主要用于测评D-Robotics 混合异构模型的推理性能情况，D-Robotics 提供了模型性能评估的工具，您可以使用这些工具验证模型性能是否达到应用要求。具体使用说明，请阅读 [**模型性能分析与调优**](#performance_evaluation)章节内容。",
        "**Performance Evaluation** This stage mainly evaluates the inference performance of D-Robotics hybrid heterogeneous models. D-Robotics provides model performance evaluation tools. You can use these tools to verify whether model performance meets application requirements. For detailed instructions, please read the [**Model Performance Analysis and Tuning**](#performance_evaluation) section.",
    ),
    (
        "**精度评估** 本阶段主要用于测评D-Robotics 混合异构模型的推理精度情况，D-Robotics 提供了模型精度评估的工具。具体使用说明，请阅读[**模型精度分析与调优**](#accuracy_evaluation)章节内容。",
        "**Accuracy Evaluation** This stage mainly evaluates the inference accuracy of D-Robotics hybrid heterogeneous models. D-Robotics provides model accuracy evaluation tools. For detailed instructions, please read the [**Model Accuracy Analysis and Tuning**](#accuracy_evaluation) section.",
    ),
    ("### 模型准备{#model_preparation}", "### Floating-Point Model Preparation{#model_preparation}"),
    (
        "基于公开DL框架训练得到的浮点模型是D-Robotics 模型转换工具的输入，目前转换工具支持的DL框架如下：",
        "Floating-point models trained with public DL frameworks are the input to the D-Robotics model conversion tool. The DL frameworks currently supported by the conversion tool are as follows:",
    ),
    (
        "以上框架中， Caffe框架导出的caffemodel是直接支持的，PyTorch、TensorFlow和MXNet等DL框架通过转换到ONNX格式间接支持。",
        "Among the frameworks above, caffemodel exported from the Caffe framework is directly supported. DL frameworks such as PyTorch, TensorFlow, and MXNet are indirectly supported by converting to ONNX format.",
    ),
    (
        "对于不同框架到ONNX的转换，目前都有对应的标准化方案，参考如下：",
        "Standardized solutions are available for converting different frameworks to ONNX. Refer to the following:",
    ),
    (
        "-    Pytorch2Onnx：PytTorch官方API支持直接将模型导出为ONNX模型，参考链接：",
        "-    Pytorch2Onnx: The PyTorch official API supports exporting models directly to ONNX. Reference link:",
    ),
    (
        "-    Tensorflow2Onnx：基于ONNX社区的onnx/tensorflow-onnx 进行转换，参考链接：",
        "-    Tensorflow2Onnx: Convert using onnx/tensorflow-onnx from the ONNX community. Reference link:",
    ),
    (
        "-    MXNet2Onnx：MXNet官方API支持直接将模型导出为ONNX模型，参考链接：",
        "-    MXNet2Onnx: The MXNet official API supports exporting models directly to ONNX. Reference link:",
    ),
    (
        "-    更多框架的ONNX转换支持，参考链接：",
        "-    For ONNX conversion support for more frameworks, reference link:",
    ),
    (
        "  关于Pytorch、PaddlePaddle、TensorFlow2框架的模型，我们也提供了如何导出ONNX及模型可视化的教程，请参考：",
        "  For models from PyTorch, PaddlePaddle, and TensorFlow2 frameworks, we also provide tutorials on exporting ONNX and model visualization. Please refer to:",
    ),
    (
        "  - [**Pytorch导出ONNX及模型可视化教程**](https://developer.d-robotics.cc/forumDetail/146177165367615499) ；",
        "  - [**PyTorch ONNX Export and Model Visualization Tutorial**](https://developer.d-robotics.cc/forumDetail/146177165367615499) ;",
    ),
    (
        "  - [**PaddlePaddle导出ONNX及模型可视化教程**](https://developer.d-robotics.cc/forumDetail/146177165367615500) ；",
        "  - [**PaddlePaddle ONNX Export and Model Visualization Tutorial**](https://developer.d-robotics.cc/forumDetail/146177165367615500) ;",
    ),
    (
        "  - [**TensorFlow2导出ONNX及模型可视化教程**](https://developer.d-robotics.cc/forumDetail/146177165367615501) ；",
        "  - [**TensorFlow2 ONNX Export and Model Visualization Tutorial**](https://developer.d-robotics.cc/forumDetail/146177165367615501) ;",
    ),
    (
        "  - 浮点模型中所使用的算子需要符合D-Robotics 算法工具链的算子约束条件，具体请阅读 [**模型算子支持列表**](./supported_op_list) 章节进行查询。",
        "  - Operators used in the floating-point model must comply with the operator constraints of the D-Robotics algorithm toolchain. Please refer to the [**Model Operator Support List**](./supported_op_list) section for details.",
    ),
    (
        "  - 目前转换工具仅支持输出个数小于或等于32的模型进行转换。",
        "  - Currently, the conversion tool only supports models with 32 or fewer outputs.",
    ),
    (
        "  - 支持 ``caffe 1.0`` 版本的caffe浮点模型和 ``ir_version≤7`` , ``opset=10`` 、 ``opset=11`` 版本的onnx浮点模型量化成D-Robotics 支持的定点模型, onnx模型的ir_version与onnx版本的对应关系请参考[**onnx官方文档**](https://github.com/onnx/onnx/blob/main/docs/Versioning.md) ；",
        "  - Supports quantizing Caffe floating-point models of ``caffe 1.0`` and ONNX floating-point models with ``ir_version≤7``, ``opset=10``, and ``opset=11`` into fixed-point models supported by D-Robotics. For the correspondence between ONNX model ir_version and ONNX version, please refer to the [**ONNX official documentation**](https://github.com/onnx/onnx/blob/main/docs/Versioning.md) ;",
    ),
    (
        "  - 模型输入维度只支持 ``固定4维`` 输入NCHW或NHWC（N维度只能为1），例如：1x3x224x224或1x224x224x3， 不支持动态维度及非4维输入；",
        "  - Model input dimensions only support ``fixed 4-dimensional`` NCHW or NHWC input (N dimension must be 1), for example: 1x3x224x224 or 1x224x224x3. Dynamic dimensions and non-4-dimensional inputs are not supported;",
    ),
    (
        "  - 浮点模型中不要包含有 ``后处理算子``，例如：nms算子。",
        "  - Do not include ``post-processing operators`` in the floating-point model, such as the NMS operator.",
    ),
]

# Apply section translations
for zh, en in SECTION_TRANSLATIONS:
    text = text.replace(zh, en)

# Structural / pattern replacements
PATTERN_REPLACEMENTS = [
    (r":::tip 小技巧", ":::tip Tip"),
    (r":::caution 注意", ":::caution Note"),
    (r":::info 备注", ":::info Note"),
    (r"\| 参数名称 \| 参数配置说明\s+\| 取值范围说明 \|    可选/必选\s+\|",
     "| Parameter Name | Parameter Description | Value Range | Optional/Required |"),
    (r"\| \*\*框架\*\*", "| **Framework**"),
    (r"\| \*\*D-Robotics 工具链\*\* \| 支持", "| **D-Robotics Toolchain** | Supported"),
    (r"支持（转ONNX）", "Supported (convert to ONNX)"),
    (r"\|可选 \|", "|Optional |"),
    (r"\|必选 \|", "|Required |"),
    (r"\*\*参数作用\*\*", "**Purpose**"),
    (r"\*\*参数说明\*\*", "**Description**"),
    (r"\*\*取值范围\*\*", "**Value Range**"),
    (r"\*\*默认配置\*\*", "**Default**"),
    (r"\*\*注意：\*\*", "**Note:**"),
    (r"\*\*功能\*\*", "**Function**"),
    (r"\*\*命令行格式\*\*", "**Command-Line Format**"),
    (r"\*\*参数组\*\*", "**Parameters**"),
    (r"\*\*分析结果展示\*\*", "**Analysis Result**"),
    (r"\*\*描述\*\*", "**Description**"),
    (r"函数使用方法：", "Function usage:"),
    (r"命令行使用方法：", "Command-line usage:"),
    (r"函数返回值：", "Function return value:"),
    (r"API使用方法：", "API usage:"),
    (r"API函数使用方法：", "API function usage:"),
    (r"- 使用方法", "- Usage"),
    (r"- 命令行参数", "- Command-Line Parameters"),
    (r"- 输出内容说明", "- Output Description"),
    (r"- 使用方式", "- Usage"),
]

for pattern, repl in PATTERN_REPLACEMENTS:
    text = re.sub(pattern, repl, text)

# Write intermediate result and report
cn_remaining = len(re.findall(r"[\u4e00-\u9fff]", text))
print(f"After partial translation, remaining Chinese characters: {cn_remaining}")

# Save partial output for inspection
partial = ROOT / "scripts" / "ptq_process_partial_en.md"
partial.write_text(text, encoding="utf-8")
print(f"Partial output written to {partial}")
