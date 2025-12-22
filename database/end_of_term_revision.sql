/*
 Navicat Premium Dump SQL

 Source Server         : WSL_MySQL
 Source Server Type    : MySQL
 Source Server Version : 80044 (8.0.44-0ubuntu0.24.04.1)
 Source Host           : 172.31.142.67:3306
 Source Schema         : end_of_term_revision

 Target Server Type    : MySQL
 Target Server Version : 80044 (8.0.44-0ubuntu0.24.04.1)
 File Encoding         : 65001

 Date: 22/12/2025 14:12:47
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for db_configs
-- ----------------------------
DROP TABLE IF EXISTS `db_configs`;
CREATE TABLE `db_configs`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '数据库配置 ID',
  `user_id` bigint NOT NULL COMMENT '所属用户 ID',
  `db_host` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '数据库主机地址',
  `db_port` int NOT NULL COMMENT '数据库端口号',
  `db_user` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '数据库用户名',
  `db_password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '数据库密码',
  `db_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '数据库名',
  `is_active` tinyint(1) NULL DEFAULT 0 COMMENT '是否是当前使用的数据库配置',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `db_configs_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 1 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户自定义数据库配置表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for error_book
-- ----------------------------
DROP TABLE IF EXISTS `error_book`;
CREATE TABLE `error_book`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '错题记录 ID',
  `user_id` bigint NOT NULL COMMENT '用户 ID',
  `subject_id` bigint NOT NULL COMMENT '科目 ID',
  `question_id` bigint NOT NULL COMMENT '题目 ID',
  `wrong_count` int NULL DEFAULT 1 COMMENT '累计错误次数',
  `last_wrong_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '最后错误时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `user_id`(`user_id` ASC, `subject_id` ASC, `question_id` ASC) USING BTREE,
  INDEX `subject_id`(`subject_id` ASC) USING BTREE,
  INDEX `question_id`(`question_id` ASC) USING BTREE,
  CONSTRAINT `error_book_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `error_book_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `error_book_ibfk_3` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 19 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '错题集表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for llm_models
-- ----------------------------
DROP TABLE IF EXISTS `llm_models`;
CREATE TABLE `llm_models`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '模型配置 ID',
  `user_id` bigint NOT NULL COMMENT '所属用户 ID',
  `model_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模型名称',
  `base_url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '模型 API 地址',
  `api_key` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT 'API 密钥',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `llm_models_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '用户自定义大模型配置表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for practice_records
-- ----------------------------
DROP TABLE IF EXISTS `practice_records`;
CREATE TABLE `practice_records`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '练习记录 ID',
  `session_id` bigint NULL DEFAULT NULL COMMENT '练习会话 ID',
  `user_id` bigint NOT NULL COMMENT '用户 ID',
  `subject_id` bigint NOT NULL COMMENT '科目 ID',
  `question_id` bigint NOT NULL COMMENT '题目 ID',
  `user_answer` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户作答',
  `is_correct` tinyint(1) NOT NULL COMMENT '是否正确 1=正确 0=错误',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作答时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  INDEX `subject_id`(`subject_id` ASC) USING BTREE,
  INDEX `question_id`(`question_id` ASC) USING BTREE,
  INDEX `idx_session_id`(`session_id` ASC) USING BTREE,
  CONSTRAINT `practice_records_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `practice_records_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `practice_records_ibfk_3` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `practice_records_ibfk_4` FOREIGN KEY (`session_id`) REFERENCES `practice_sessions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 39 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '练习记录表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for practice_sessions
-- ----------------------------
DROP TABLE IF EXISTS `practice_sessions`;
CREATE TABLE `practice_sessions`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '练习会话 ID',
  `user_id` bigint NOT NULL COMMENT '用户 ID',
  `subject_id` bigint NOT NULL COMMENT '科目 ID',
  `total_count` int NOT NULL COMMENT '总题数',
  `correct_count` int NOT NULL COMMENT '正确题数',
  `wrong_count` int NOT NULL COMMENT '错误题数',
  `accuracy` decimal(5, 2) NOT NULL COMMENT '正确率',
  `grade` varchar(10) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '成绩等级 A/B/C/D/F',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '练习时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_user_subject`(`user_id` ASC, `subject_id` ASC) USING BTREE,
  INDEX `idx_created_at`(`created_at` ASC) USING BTREE,
  INDEX `practice_sessions_ibfk_2`(`subject_id` ASC) USING BTREE,
  CONSTRAINT `practice_sessions_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `practice_sessions_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 6 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '练习会话表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for question_resources
-- ----------------------------
DROP TABLE IF EXISTS `question_resources`;
CREATE TABLE `question_resources`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '资源ID',
  `question_id` bigint NOT NULL COMMENT '关联题目ID',
  `resource_type` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '资源类型：image/table_json/diagram_desc/other',
  `resource_content` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '资源内容：图片URL或JSON数据',
  `resource_order` int NULL DEFAULT 0 COMMENT '资源显示顺序',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `idx_question_id`(`question_id` ASC) USING BTREE,
  INDEX `idx_resource_type`(`resource_type` ASC) USING BTREE,
  CONSTRAINT `question_resources_ibfk_1` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '题目资源表' ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for questions
-- ----------------------------
DROP TABLE IF EXISTS `questions`;
CREATE TABLE `questions`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '题目 ID',
  `subject_id` bigint NOT NULL COMMENT '科目 ID',
  `user_id` bigint NOT NULL COMMENT '用户 ID',
  `type` enum('single','multiple','judge','fill','major') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题目类型',
  `question` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '题干内容',
  `options_json` json NULL COMMENT '选项 JSON',
  `answer` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '正确答案',
  `analysis` text CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '解析',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  INDEX `subject_id`(`subject_id` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `questions_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `questions_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 138 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '题库表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for subject_shares
-- ----------------------------
DROP TABLE IF EXISTS `subject_shares`;
CREATE TABLE `subject_shares`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '共享记录ID',
  `owner_user_id` bigint NOT NULL COMMENT '科目拥有者ID',
  `subject_id` bigint NOT NULL COMMENT '被共享的科目ID',
  `target_user_id` bigint NULL DEFAULT NULL COMMENT '被共享给的用户ID（NULL表示公共共享）',
  `share_type` enum('USER','PUBLIC') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '共享类型：USER=指定用户，PUBLIC=公共',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `unique_share`(`subject_id` ASC, `target_user_id` ASC, `share_type` ASC) USING BTREE,
  INDEX `idx_subject_id`(`subject_id` ASC) USING BTREE,
  INDEX `idx_target_user`(`target_user_id` ASC) USING BTREE,
  INDEX `idx_owner`(`owner_user_id` ASC) USING BTREE,
  CONSTRAINT `subject_shares_ibfk_1` FOREIGN KEY (`owner_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `subject_shares_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT,
  CONSTRAINT `subject_shares_ibfk_3` FOREIGN KEY (`target_user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '科目共享表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for subjects
-- ----------------------------
DROP TABLE IF EXISTS `subjects`;
CREATE TABLE `subjects`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '科目ID',
  `user_id` bigint NOT NULL COMMENT '所属用户 ID',
  `name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '科目名称',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `name`(`name` ASC, `user_id` ASC) USING BTREE,
  INDEX `user_id`(`user_id` ASC) USING BTREE,
  CONSTRAINT `subjects_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE RESTRICT
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '科目表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for system_config
-- ----------------------------
DROP TABLE IF EXISTS `system_config`;
CREATE TABLE `system_config`  (
  `id` int NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `config_key` varchar(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NOT NULL COMMENT '配置键名(唯一)',
  `config_value` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci NULL COMMENT '配置值(JSON格式)',
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `config_key`(`config_key` ASC) USING BTREE,
  INDEX `idx_config_key`(`config_key` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci COMMENT = '系统配置表' ROW_FORMAT = DYNAMIC;

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT '用户主键 ID',
  `username` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '用户名（唯一）',
  `password_hash` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL COMMENT '密码哈希值（加密存储）',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`id`) USING BTREE,
  UNIQUE INDEX `username`(`username` ASC) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 3 CHARACTER SET = utf8mb4 COLLATE = utf8mb4_0900_ai_ci COMMENT = '系统用户表' ROW_FORMAT = DYNAMIC;

SET FOREIGN_KEY_CHECKS = 1;
