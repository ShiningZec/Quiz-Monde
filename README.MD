# Quiz-Monde

Quiz-Monde 是一个集成了 **问答**、**Quiz 题库**、**Quiz 导入**、**AI 生成 Quiz** 等功能的 **Quiz 引擎**。

## Get-Started

你只需要安装依赖，然后执行 `app.py` 即可。

```sh
# run (venv)
python -m venv .venv
pip install -r requirements.txt
# and run
python app.py
```

## 如何贡献此项目？

### 项目逻辑结构

```text
Quiz-Monde
│
├── Quiz  # 如何表示 Quiz 的逻辑结构
│     ├── SingleChoice
│     ├── MultipleChoice
│     ├── ShortAnswer
│     └── ImageQuiz
│
├── QuizCollection  # 如何组织 Quiz
│
├── UserAnswer  # 用户如何回答
│
├── QuizSession  # 如何像用户展示 Quiz
│
├── Statistics  # 答题结果的展示
│
├── AIQuizGenerator  # 引入 AI 生成 Quiz
│
└── Storage  # Quiz 等资源的储存
      └── JSON
```

### 文件结构

```text
Quiz-Monde
│
├── assets  # 基本资源的储存
│     └── Icons  # 手写板使用的图标
│
├── dataset  # Quiz 资源的储存
│     └── *.json  # Quiz 文件
│
├── src  # 各个代码模块
│     ├── __init__.py
│     ├── contentBlock.py  # 描述了 Quiz 如何拆分 metadata 以用于展示的类。
│     ├── handWriting.py  # 一个手动实现的手写板，继承自 QWidget。
│     ├── prompt.py  # 描述了向 AI 搜索使用的提示词。
│     ├── quiz.py  # 约束一个 quiz 需要拥有的标识、内容；约束一个 QuizRequest 需要拥有的标识。
│     ├── quizLoader.py  # 从 json 文件或递归从文件夹获取 quiz 的类。
│     ├── quizLoaderAI.py  # 从 AI 获取 quiz 的类。
│     └── quizLoaderAI.pyi  # 描述 quizLoaderAI.py 的接口；方便用户编写面向其他 AI 的类。
│
├── app.py  # 代码主程序以及入口
│
└── config.json  # 用户的 API_KEY 等信息的存放位置。
```
