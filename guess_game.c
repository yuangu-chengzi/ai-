#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

#ifdef _WIN32
#include <windows.h>
#endif

// 改进的JSON解析器
// 完全重写的JSON解析函数
// 修复后的JSON解析函数 - 移除调试信息
void parse_simple_json(const char* json, char* item, char hints[5][100]) {
    // 初始化
    item[0] = '\0';
    for (int i = 0; i < 5; i++) {
        hints[i][0] = '\0';
    }
    
    // 解析item
    const char* item_ptr = strstr(json, "\"item\"");
    if (item_ptr) {
        item_ptr = strstr(item_ptr, ":");
        if (item_ptr) {
            item_ptr++; // 跳过冒号
            // 跳过空格
            while (*item_ptr == ' ') item_ptr++;
            // 找开始引号
            if (*item_ptr == '\"') {
                item_ptr++; // 跳过引号
                const char* item_end = strchr(item_ptr, '\"');
                if (item_end) {
                    int len = item_end - item_ptr;
                    if (len > 0 && len < 100) {
                        strncpy(item, item_ptr, len);
                        item[len] = '\0';
                    }
                }
            }
        }
    }
    
    // 解析hints
    const char* hints_ptr = strstr(json, "\"hints\"");
    if (hints_ptr) {
        hints_ptr = strstr(hints_ptr, "[");
        if (hints_ptr) {
            hints_ptr++; // 跳过 [
            int hint_index = 0;
            
            while (hint_index < 5) {
                // 找提示的开始引号
                while (*hints_ptr && *hints_ptr != '\"') hints_ptr++;
                if (*hints_ptr != '\"') break; // 没有找到引号，退出
                
                hints_ptr++; // 跳过引号
                const char* hint_end = strchr(hints_ptr, '\"');
                if (!hint_end) break; // 没有找到结束引号，退出
                
                // 提取提示内容
                int len = hint_end - hints_ptr;
                if (len > 0 && len < 100) {
                    strncpy(hints[hint_index], hints_ptr, len);
                    hints[hint_index][len] = '\0';
                    hint_index++;
                }
                
                hints_ptr = hint_end + 1; // 移动到下一个提示
            }
        }
    }
    
    // 注意：这里移除了所有的printf调试信息！
}
void parse_check_result(const char* json, char* is_correct, char* feedback) {
    strcpy(is_correct, "false");
    strcpy(feedback, "Try again");
    
    // 解析is_correct
    const char* correct_ptr = strstr(json, "\"is_correct\"");
    if (correct_ptr) {
        correct_ptr = strstr(correct_ptr, ":");
        if (correct_ptr) {
            correct_ptr++;
            while (*correct_ptr == ' ') correct_ptr++;
            
            if (strncmp(correct_ptr, "true", 4) == 0) {
                strcpy(is_correct, "true");
            }
        }
    }
    
    // 解析feedback
    const char* feedback_ptr = strstr(json, "\"feedback\"");
    if (feedback_ptr) {
        feedback_ptr = strstr(feedback_ptr, ":");
        if (feedback_ptr) {
            feedback_ptr++;
            while (*feedback_ptr && *feedback_ptr != '\"') feedback_ptr++;
            if (*feedback_ptr == '\"') {
                feedback_ptr++;
                const char* feedback_end = strstr(feedback_ptr, "\"");
                if (feedback_end) {
                    int len = feedback_end - feedback_ptr;
                    if (len > 0 && len < 200) {
                        strncpy(feedback, feedback_ptr, len);
                        feedback[len] = '\0';
                    }
                }
            }
        }
    }
    
    // 注意：这里也移除了调试信息！
}
void call_python(const char* command, char* output, int max_len) {
    char full_command[512];
    snprintf(full_command, sizeof(full_command), "python item_game.py %s", command);
    
    FILE* fp = popen(full_command, "r");
    if (fp == NULL) {
        strcpy(output, "{}");
        return;
    }
    
    if (fgets(output, max_len, fp) == NULL) {
        strcpy(output, "{}");
    }
    pclose(fp);
    
    output[strcspn(output, "\n")] = 0;
}
int main() {
#ifdef _WIN32
    // 设置控制台为UTF-8编码
    SetConsoleOutputCP(65001);
    SetConsoleCP(65001);
#endif

    char json_output[1024];
    char secret_item[100];
    char hints[5][100];
    char user_guess[100];
    char feedback[200];
    char is_correct[10];
    
    printf("=== AI Guess Game ===\n");
    printf("Guess the object! Type 'quit' to exit\n\n");
    
    // 生成物品
    printf("Generating item...");
    call_python("generate", json_output, sizeof(json_output));
    parse_simple_json(json_output, secret_item, hints);
    printf("Ready!\n\n");
    
    int hints_given = 0;
    int max_hints = 5;
    int game_over = 0;
    
    while (!game_over && hints_given < max_hints) {
        // 显示线索
        printf("Hints (%d/%d):\n", hints_given + 1, max_hints);
        for (int i = 0; i <= hints_given; i++) {
            if (strlen(hints[i]) > 0) {
                printf("%d. %s\n", i + 1, hints[i]);
            }
        }
        
        printf("\nYour guess: ");
        fgets(user_guess, sizeof(user_guess), stdin);
        user_guess[strcspn(user_guess, "\n")] = 0;
        
        if (strcmp(user_guess, "quit") == 0) {
            printf("Game ended. Answer was: %s\n", secret_item);
            break;
        }
        
        if (strlen(user_guess) == 0) {
            continue;
        }
        
        // 检查猜测
        char command[512];
        snprintf(command, sizeof(command), "check \"%s\" \"%s\"", secret_item, user_guess);
        call_python(command, json_output, sizeof(json_output));
        parse_check_result(json_output, is_correct, feedback);
        
        printf("\n%s\n\n", feedback);
        
        if (strcmp(is_correct, "true") == 0) {
            printf("*** Congratulations! You win! ***\n");
            game_over = 1;
        } else {
            hints_given++;
            if (hints_given >= max_hints) {
                printf("Game over! The answer was: %s\n", secret_item);
            } else {
                printf("Here's another hint...\n\n");
            }
        }
    }
    
    printf("Thanks for playing!\n");
    return 0;
}