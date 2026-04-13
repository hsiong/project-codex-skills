更新该规范  java 代码规范， 生成java相关代码时需要参考本skill

1. 尽量避免重复代码，没有必要提出来单独做方法的，就写一整个大方法
2. 需要结合 @param @return 完成方法注释
3. 关键代码需要注释
4. 接口只调用方法，具体逻辑写在service中
5. 不是数据库 CRUD 的代码，无需使用 service impl，直接用 class service 即可。
6. DTO Entity Pojo 等实体字段，需要使用 @Schema 描述；实体本身使用 @Data
7. Controller
   - 使用 @Operation，
   - 优先使用 Post 请求，
   - 查询接口以 getXXX 命名，
   - 返回使用 Result 类
8. requestDTO 必填的值，应使用 @NotBlank 或者 @NotNull,  并填入 message xxx不能为空
