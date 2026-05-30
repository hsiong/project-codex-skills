---
name: python-code-style
description: "当用户要生成、补全、修改或评审 Python 代码时触发。它按现有项目风格做最小必要改动；不用于前端、纯运维或需要大规模重构的任务。"
---

# Python Code Style

按下面规则生成 Python 代码，并优先兼容用户当前项目已有风格；如果项目已有写法与本 skill 不冲突，保持一致。

+ 框架默认使用 `fastapi`

## FastAPI 与接口代码

- 路由层只负责接收参数、调用 service 或核心逻辑、返回结果。
- 具体业务判断、数据拼装、状态处理放在 service 或业务方法中。
- 请求体、响应体优先使用 Pydantic 模型描述。
- 新增接口时保持函数命名清晰，参数和返回结构稳定。
- 具体方法应写到 service或者core中  , api中禁止写任何方法实现

## SQL 与 ORM
用户要求 '入库' '持久化' 等操作, 参考本规范
+ SQL 数据库默认使用 postgres, 参考 `postgres_init.py`
+ ORM 使用 SQLAlchemy
+ ORM Entity crud 链路存到 `model` 目录下, `model/repo, entity, service/xxx`
+ Entity model 需要兼容 `SQLAlchemy` 模型定义
+ `SQLAlchemy` 模型定义完全兼容 `pydantic`模型吗? 如果不兼容,  完成 `pydantic` 和 `SQLAlchemy` 模型互转方法
  + 如果读取的 `POSTGRES_URL` 为空, 则不 import SQLAlchemy 相关类, 避免报错
  + 因为很多项目无需 SQLAlchemy
+ `repo` 只负责实现最基础的 `add update delete list`, `service` 负责业务逻辑

## 实体与请求对象
- 基于 `pydantic` 模型定义 
- 接口使用以下解析
  ```
      request_dict: BotAnalyseApiRequest = BotAnalyseApiRequest.model_validate(
        request_json
    )
  ```
- 一批业务会有多个 `model`, 分别命名为 _dto、_vo、_request
- 新增文件位于 `model/xxx` 目录下, 文件命名为 `业务_xxx`


## 方法

- 已有方法需要新增业务参数时，优先在当前真实调用点直接补齐参数，保持调用链最短。
- 多个代码块有复用代码的，抽离为工具类或私有方法，避免重复代码
- 重点: 没有复用的代码, 禁止单独抽成方法, 除非这个代码块有明显的业务含义并超过了 50 行
- 尽量避免冗余设计, 优先选择直接实现，避免无实际价值的抽象和中间层
  - 如果两个方法(包括CRUD)的唯一区别只是传入不同的 `true/false`、常量、枚举或字符串，优先合并为一个真实方法，由调用方直接传参。
  - 禁止新增只有一层转发、没有独立业务语义的包装方法。
  - 禁止为了透传新增参数而连续新增一堆没有任何用途的重载方法。 
  - 禁止出现“旧方法只调用新方法并补 null/false/default 参数”的包装式重载，除非用户明确要求兼容旧调用。
  - 纯CRUD且没有超过两次的调用, 直接使用 mapper
- 同一批业务只能放到 `core` 同一个文件内, API 路由只从一个 core 文件导入方法

## 变更边界

- 禁止修改与用户当前需求无关的代码、配置占位符、注释、格式、命名、依赖、接口 URL、调度表达式等内容。即使发现现有代码看起来不够优雅、不够一致、可能有更好的写法，也只能在回复中提示，不得顺手修改。
- 新增代码时优先做最小必要改动，不顺手扩展范围，不主动重构整条链路
- 除非用户明确要求，直接修改相关代码即可
- 能直接返回就直接返回，避免无意义的中间变量和多层嵌套。
- 如果文件移动后, 之前的目录为空, 则删除之前的目录

## 注释

- 变量名、函数名、类名要直接表达业务含义，不使用过度缩写。
- 关键分支、边界处理、数据转换要补充简洁注释，不写逐行翻译式注释。
- 注释直接说明业务目的和入参与返回关系，不写空泛表述。
- 生成注释时，优先解释“为什么这样处理”，不是重复代码字面意思。
- 关键代码必须加注释，重点解释业务判断、分支原因、边界处理和数据转换，不写无意义的逐行注释。

## 测试代码约定

- 如果用户要求生成测试方法，实现逻辑必须非常简单，方便直接运行和理解。
- 不要使用 `add_argument` 这类命令行参数解析方式包装测试入参，直接使用普通变量。
- 测试优先覆盖主流程、关键分支和明显边界，不写过度复杂的构造逻辑。
- 除了 dify 等高星项目, 除非用户明确要求, 不要mock, 而是实际测试
  - 不使用 `Mock客户端`, 而是调用实际接口/执行实际业务
  - 不使用 `Mock数据`, 而是按接口业务, 传入实际文件/数据
- 测试的相关类也要符合 `## 实体与请求对象` 的约定
- 除非用户明确要求，禁止你自动测试
- 除非用户明确要求，不需要你自动验证, 只需要你自动编译检查有无语法问题


## 依赖
- 依赖需要加入版本
- 除非用户明确要求，依赖文件中如果缺乏 `-i https://pypi.tuna.tsinghua.edu.cn/simple`, 自动补充
- 禁止自动修改依赖文件名称

## 配置项约束

- 禁止访问任何 `config/.env.*` 文件
- 新增的配置项，放到 `config/settings.py` 中, 比如 `POSTGRES_URL = env.get("POSTGRES_URL")`, 
  + 除非用户要求, 不需要默认值
- 新增的具体配置, 直接在 terminal 日志中打印新增 key 和建议值, 比如 `POSTGRES_URL=xxx`
- 如需使用常量, 放到 `config` 文件夹下合适的类中

## 强约束

- 只做提交相关操作，不改用户代码，不顺手修问题，不整理格式。
- 只允许查看 Git 已知路径：已跟踪改动、已暂存新增、已暂存删除。真正未跟踪文件一律不访问。
- 禁止使用 `git add .`、`git add -A`、`git commit -a` 这类会扩大范围的命令。
- 禁止读取或提交以下内容：
  - `*/.mvn/*`
  - `*/.idea/*`
  - `config/.env.*`
  - `.gitignore` 中提到的内容
- 读取 `.gitignore`。禁止访问和提交 .gitignore 内提到的内容
- 没有加入到 git 管理中的文件，禁止你访问和自行添加，禁止执行 `git add`命令
- 如果变更的代码中存在 `todo`，必须提醒用户(哪个文件：哪行代码)，并终止后续提交


## 核心规范

- 先理解现有文件风格，再补全或修改代码。
- 生成的代码应可直接落地，避免只写空壳、TODO 或伪代码。
- 使用框架内已有的日志工具
- 除非用户要求, 已存在的文件/代码/注释, 禁止你删除
- 新增的文件自动 `git add`
- 除非用户明确要求, 禁止使用 `Map`
- Avoid passing complex expressions, chained calls, or request getters directly into method parameters. Extract method inputs into clearly named local variables first, then pass those variables to the method. This makes the business meaning of each parameter explicit, improves readability, and makes future validation, logging, debugging, and null checks easier.
- 缩进使用 tab
- keep indents on empty lines
- 除非用户要求, 禁止使用 `async`/`await`
- 相对路径是项目项目路径, 不是 agent 相对路径 !