import pygame
import threading
import openai
from PIL import Image
from button_utils import draw_return_button
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, GRAY, FONT_PATH

# Configure OpenAI API
openai.api_base = "http://chatapi.littlewheat.com/v1"
openai.api_key = "APIkey"

bg_image = pygame.image.load("./bg/bg2.jpg")
bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

result_image = pygame.image.load("./bg/result.png")
result_image = pygame.transform.scale(result_image, (int(SCREEN_WIDTH * 0.9), int(SCREEN_HEIGHT * 0.9)))
result_image_rect = result_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

result_visible = False  # 是否显示结果图片

view_result_image = pygame.image.load("./png/view_result.png")
view_result_hover_image = pygame.transform.scale(
    view_result_image, (int(view_result_image.get_width() * 1.1), int(view_result_image.get_height() * 1.1))
)

# 提交按钮适配屏幕大小
submit_button_width = SCREEN_WIDTH //4.4
submit_button_height = SCREEN_HEIGHT //5.2
view_result_image = pygame.transform.scale(view_result_image, (submit_button_width, submit_button_height))
view_result_hover_image = pygame.transform.scale(
    view_result_hover_image, (int(submit_button_width * 1.1), int(submit_button_height * 1.1))
)
submit_button_rect = pygame.Rect(SCREEN_WIDTH // 2 - submit_button_width // 2, SCREEN_HEIGHT // 4 + 200, submit_button_width, submit_button_height)

# 加载 loading 动图帧 (仅从第二帧到倒数第二帧)
loading_gif_image = Image.open("./gif/loading.gif")
loading_frames = []
loading_durations = []
original_width, original_height = loading_gif_image.size
translate_loading_scale = 0.5
scaled_width = int(original_width * translate_loading_scale)
scaled_height = int(original_height * translate_loading_scale)

for frame in range(1, loading_gif_image.n_frames - 1):  # 从第二帧到倒数第二帧
    loading_gif_image.seek(frame)
    frame_image = pygame.image.fromstring(loading_gif_image.tobytes(), loading_gif_image.size, loading_gif_image.mode)
    frame_image = pygame.transform.scale(frame_image, (scaled_width, scaled_height))  # 缩小为 30%
    loading_frames.append(frame_image)
    loading_durations.append(loading_gif_image.info.get("duration", 100))  # 每帧持续时间（毫秒）
translate_loading_scale = 1

# 加载返回按钮图片
back_image = pygame.image.load("./png/back.png")
back_hover_image = pygame.transform.scale(back_image, (int(back_image.get_width() * 1.1), int(back_image.get_height() * 1.1)))

# 自适应屏幕的缩放比例
back_button_width = SCREEN_WIDTH // 11
back_button_height = SCREEN_HEIGHT // 10
back_image = pygame.transform.scale(back_image, (back_button_width, back_button_height))
back_hover_image = pygame.transform.scale(back_hover_image, (int(back_button_width * 1.1), int(back_button_height * 1.1)))

# 创建按钮矩形
back_button_rect = pygame.Rect(20, 20, back_button_width, back_button_height)

translate_button_image = pygame.image.load("./png/trans.png")
translate_button_hover_image = pygame.transform.scale(
    translate_button_image, (int(translate_button_image.get_width() * 1.1), int(translate_button_image.get_height() * 1.1))
)

# 翻译按钮大小适配屏幕
translate_button_width = SCREEN_WIDTH //10
translate_button_height = SCREEN_HEIGHT //24
translate_button_image = pygame.transform.scale(translate_button_image, (translate_button_width, translate_button_height))
translate_button_hover_image = pygame.transform.scale(
    translate_button_hover_image, (int(translate_button_width * 1.1), int(translate_button_height * 1.1))
)

# 初始化按钮矩形，位置为结果图片下方
translate_button_rect = pygame.Rect(
    result_image_rect.right // 2,
    result_image_rect.top + 25,
    translate_button_width,
    translate_button_height,
)

# 状态变量
loading = False
response_text = ""
response_ready = True
loading_frame_index = 0  # 动画当前帧索引
last_loading_update = 0  # 上一次更新动画帧的时间
response_text_en = ""
response_text_zh = ""

current_language = "zh"  # 当前语言，默认中文
original_result = ""  # 原始中文结果
translated_result = ""  # 翻译后的英文结果
translate_in_progress = False  # 翻译是否正在进行
translate_done_en = False
translate_done_zh = False

# Hexagram generation function
def generate_hexagram(numbers):
    if len(numbers) != 3:
        return "请输入三个三位数数字！ Please enter three three-digit numbers!"
    if not all(100 <= num <= 999 for num in numbers):
        return "每个数字必须是三位数！ Each number must be three digits!"
    lower_trigram = numbers[0] % 8
    upper_trigram = numbers[1] % 8
    changing_line = numbers[2] % 6
    return {"lower_trigram": lower_trigram, "upper_trigram": upper_trigram, "changing_line": changing_line}


# Call OpenAI API for divination
def ask_openai_api(question, hexagram, callback):
    def request_thread():
        try:
            prompt = f"""
            你是一位精通《易经》的占卜专家。以下是用户输入的信息，请基于这些内容提供占卜解读和建议：
            问题：{question}
            下卦：{hexagram['lower_trigram']}
            上卦：{hexagram['upper_trigram']}
            变爻：{hexagram['changing_line']}
            """
            completion = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            response = completion.choices[0].message.content
            callback(response)  # Pass the response back
        except Exception as e:
            callback(f"模型请求失败：{e}")

    threading.Thread(target=request_thread).start()

def reset_divination_page():
    global loading, response_text, response_ready, result_visible
    global original_result, translated_result, current_language
    global response_text_en, response_text_zh, translate_in_progress
    global translate_done_en, translate_done_zh

    loading = False
    response_text = ""
    response_ready = True
    result_visible = False
    original_result = ""
    translated_result = ""
    response_text_en = ""
    response_text_zh = ""
    translate_in_progress = False
    translate_done_en = False
    translate_done_zh = False
    current_language = "zh"

def handle_return_events(event):
    if event.type == pygame.MOUSEBUTTONDOWN:
        if back_button_rect.collidepoint(event.pos):
            reset_divination_page()  # 重置页面状态
            return "main"  # 返回主页面状态

# Handle events for divination page
def handle_divination_events(event, text_question, text_numbers, input_active_question, input_active_numbers, api_function, callback):
    global loading, response_text, result_visible, translate_in_progress, response_text_en, response_text_zh, translate_loading_scale

    if event.type == pygame.MOUSEBUTTONDOWN:
        question_box = pygame.Rect(50, SCREEN_HEIGHT // 4, SCREEN_WIDTH - 100, 50)
        numbers_box = pygame.Rect(50, SCREEN_HEIGHT // 4 + 130, SCREEN_WIDTH - 100, 50)

        if question_box.collidepoint(event.pos):
            input_active_question = True
            input_active_numbers = False
        elif numbers_box.collidepoint(event.pos):
            input_active_numbers = True
            input_active_question = False
        elif submit_button_rect.collidepoint(event.pos) and response_ready:
            loading = True
            response_text = ""
            try:
                numbers = [int(n) for n in text_numbers.split()]
                hexagram = generate_hexagram(numbers)
                if isinstance(hexagram, str):  # 错误信息
                    callback(hexagram)
                else:
                    api_function(
                        text_question,
                        hexagram,
                        lambda resp: handle_api_response(resp, callback)
                    )
            except Exception as e:
                callback(f"输入错误：{e}")

    elif event.type == pygame.KEYDOWN and input_active_question:
        if event.key == pygame.K_RETURN:
            input_active_question = False
        elif event.key == pygame.K_BACKSPACE:
            text_question = text_question[:-1]
        else:
            text_question += event.unicode

    elif event.type == pygame.KEYDOWN and input_active_numbers:
        if event.key == pygame.K_RETURN:
            input_active_numbers = False
        elif event.key == pygame.K_BACKSPACE:
            text_numbers = text_numbers[:-1]
        elif event.unicode.isdigit() or event.unicode.isspace():  # 允许输入数字和空格
            text_numbers += event.unicode

    if event.type == pygame.MOUSEBUTTONDOWN and result_visible and translate_button_rect.collidepoint(
            event.pos) and not translate_in_progress:
        translate_loading_scale = 0.1
        translate_in_progress = True  # 开始翻译
        if current_language == "zh":
            # 翻译为英文
            ask_openai_translation(response_text, "en", lambda resp: handle_translation_response(resp, "en"))
        else:
            # 翻译回中文
            ask_openai_translation(translated_result, "zh", lambda resp: handle_translation_response(resp, "zh"))

    if event.type == pygame.MOUSEBUTTONDOWN and result_visible:
        if not result_image_rect.collidepoint(event.pos) and not translate_button_rect.collidepoint(event.pos):  # 如果点击区域不在图片范围内
            result_visible = False  # 关闭图片
            response_text = ""  # 清空结果文字
            response_text_en = ""
            response_text_zh = ""
            loading = False
    return text_question, text_numbers, input_active_question, input_active_numbers

def handle_api_response(response, callback):
    global loading, response_text, response_ready, result_visible, original_result
    loading = False
    response_ready = True
    response_text = response  # 将占卜结果赋值给 response_text
    original_result = response  # 保留原始结果
    result_visible = True  # 显示结果图片
    callback(response)

def ask_openai_translation(text, target_language, callback):
    def request_thread():
        try:
            prompt = f"""
            请将以下文字翻译成{'中文' if target_language == 'zh' else '英文'}：
            {text}
            """
            completion = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )
            response = completion.choices[0].message.content.strip()
            callback(response)  # 通过回调传递翻译结果
        except Exception as e:
            callback(f"翻译失败：{e}")

    threading.Thread(target=request_thread).start()

def handle_translation_response(response, target_language):
    global translate_in_progress, response_text_zh, response_text_en, response_text, current_language, translated_result, original_result, translate_done_en,translate_done_zh

    translate_in_progress = False  # 翻译完成
    if target_language == "en":
        translated_result = response  # 保存英文结果
        response_text_en = translated_result  # 更新为英文结果
        response_text = ""
        response_text_zh = ""
        current_language = "en"
        translate_done_en = True
        translate_done_zh = False
    else:
        response_text_zh = original_result  # 切回中文结果
        response_text = ""
        response_text_en = ""
        current_language = "zh"
        translate_done_zh = True
        translate_done_en = False

    pygame.display.update()  # 触发画布更新

# Wrap text for display
def wrap_text(surface, text, color, rect, font_path, max_font_size=12, line_spacing=5):
    font_size = max_font_size
    font = pygame.font.Font(font_path, font_size)
    line_height = font.size("Tg")[1] + line_spacing
    while True:
        font = pygame.font.Font(font_path, font_size)
        line_height = font.size("Tg")[1] + line_spacing
        max_lines = (rect.height - 20) // line_height  # 可容纳的最大行数
        lines = []  # 存储最终绘制的每一行文字

        # 分段处理：按 \n 拆分段落
        paragraphs = text.split("\n")

        for paragraph in paragraphs:
            current_line = ""  # 当前行内容

            # 对每段文字按宽度自动换行
            for char in paragraph:
                test_line = current_line + char
                if font.size(test_line)[0] <= rect.width - 100:  # 检查宽度是否超出右边界
                    current_line = test_line
                else:
                    lines.append(current_line)  # 当前行已满，存入行列表
                    current_line = char  # 将当前字符作为新行的开头

            if current_line:  # 段落末尾剩余内容
                lines.append(current_line)

        if len(lines) <= max_lines:  # 如果总行数在矩形高度范围内，完成调整
            break
        font_size -= 2  # 字体过大时减小

    x, y = rect.left + 50, rect.top + 60
    for line in lines:
        rendered_line = font.render(line, True, color)
        if y + rendered_line.get_height() > rect.bottom - 20:  # 防止文字溢出
            break
        surface.blit(rendered_line, (x, y))
        y += rendered_line.get_height() + line_spacing

# Draw the divination page
def draw_divination_page(screen, font, text_question, text_numbers, response_text, input_active_question, input_active_numbers, response_ready):
    global loading_frame_index, last_loading_update, scaled_width, scaled_height, translate_loading_scale
    screen.blit(bg_image, (0, 0))

    # 输入框和按钮位置
    question_box = pygame.Rect(50, SCREEN_HEIGHT // 4, SCREEN_WIDTH - 100, 50)
    numbers_box = pygame.Rect(50, SCREEN_HEIGHT // 4 + 130, SCREEN_WIDTH - 100, 50)

    # 绘制输入框
    pygame.draw.rect(screen, GRAY if input_active_question else (220, 220, 220), question_box, 0)
    pygame.draw.rect(screen, BLACK, question_box, 2)
    pygame.draw.rect(screen, GRAY if input_active_numbers else (220, 220, 220), numbers_box, 0)
    pygame.draw.rect(screen, BLACK, numbers_box, 2)

    if input_active_question:
        cursor_x = question_box.x + 5 + font.size(text_question)[0]
        cursor_y = question_box.y + 10
        if (pygame.time.get_ticks() // 500) % 2 == 0:  # 闪烁效果
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + 30), 2)

    if input_active_numbers:
        cursor_x = numbers_box.x + 5 + font.size(text_numbers)[0]
        cursor_y = numbers_box.y + 10
        if (pygame.time.get_ticks() // 500) % 2 == 0:  # 闪烁效果
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + 30), 2)

    # 显示提交按钮或加载动画
    if loading:
        current_time = pygame.time.get_ticks()
        # 更新动画帧
        if current_time - last_loading_update > loading_durations[loading_frame_index]:
            loading_frame_index = (loading_frame_index + 1) % len(loading_frames)
            last_loading_update = current_time
        # 显示当前帧
        loading_x = submit_button_rect.centerx - scaled_width // 2
        loading_y = submit_button_rect.centery - scaled_height // 2
        screen.blit(loading_frames[loading_frame_index], (loading_x, loading_y))
    else:
        mouse_pos = pygame.mouse.get_pos()
        if submit_button_rect.collidepoint(mouse_pos):
            screen.blit(view_result_hover_image, submit_button_rect.topleft)
        else:
            screen.blit(view_result_image, submit_button_rect.topleft)


    # 绘制返回按钮
    mouse_pos = pygame.mouse.get_pos()
    draw_return_button(screen, back_image, back_hover_image, back_button_rect, mouse_pos)

    # 绘制提示文字
    question_surface_cn = font.render("请输入问题：", True, BLACK)
    question_surface_en = font.render("Please enter a question:", True, BLACK)
    numbers_surface_cn = font.render("请输入三个三位数数字(空格隔开)：", True, BLACK)
    numbers_surface_en = font.render("Please enter three three-digit numbers (separated by spaces):", True, BLACK)
    screen.blit(question_surface_cn, (50, SCREEN_HEIGHT // 4 - 60))
    screen.blit(question_surface_en, (50, SCREEN_HEIGHT // 4 - 30))
    screen.blit(numbers_surface_cn, (50, SCREEN_HEIGHT // 4 + 70))
    screen.blit(numbers_surface_en, (50, SCREEN_HEIGHT // 4 + 100))

    # 显示输入的文字
    question_txt_surface = font.render(text_question, True, BLACK)
    numbers_txt_surface = font.render(text_numbers, True, BLACK)
    screen.blit(question_txt_surface, (question_box.x + 5, question_box.y + 10))
    screen.blit(numbers_txt_surface, (numbers_box.x + 5, numbers_box.y + 10))


    # 显示结果图片和文字
    if result_visible:
        # 绘制结果图片
        screen.blit(result_image, result_image_rect.topleft)
        wrap_text(screen, response_text, BLACK, result_image_rect, FONT_PATH)
        if translate_done_en:
            screen.blit(result_image, result_image_rect.topleft)
            wrap_text(screen, response_text_en, BLACK, result_image_rect, FONT_PATH)
        if translate_done_zh:
            screen.blit(result_image, result_image_rect.topleft)
            wrap_text(screen, response_text_zh, BLACK, result_image_rect, FONT_PATH)

        # 绘制翻译按钮
        if translate_in_progress:
            # 播放加载动画代替翻译按钮
            current_time = pygame.time.get_ticks()
            if current_time - last_loading_update > loading_durations[loading_frame_index]:
                loading_frame_index = (loading_frame_index + 1) % len(loading_frames)
                last_loading_update = current_time
            loading_x = translate_button_rect.centerx - 90
            loading_y = translate_button_rect.centery - 50
            screen.blit(loading_frames[loading_frame_index], (loading_x, loading_y))
        else:
            # 绘制翻译按钮
            if translate_button_rect.collidepoint(pygame.mouse.get_pos()):
                screen.blit(translate_button_hover_image, translate_button_rect.topleft)
            else:
                screen.blit(translate_button_image, translate_button_rect.topleft)







