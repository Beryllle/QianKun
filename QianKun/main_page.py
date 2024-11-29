import pygame
from PIL import Image
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH
from divination_page import draw_divination_page, ask_openai_api, handle_divination_events, handle_return_events
from draw_page import draw_draw_page, handle_draw_events
from calm_page import draw_calm_page, handle_calm_events

pygame.init()

# 设置窗口大小
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("QianKun")

# 定义字体
font = pygame.font.Font(FONT_PATH, 28)

# 初始化状态
current_page = "main"

# 加载并缓存 GIF 背景帧
bg_gif_path = "./gif/bg.gif"
bg_gif_image = Image.open(bg_gif_path)
bg_frames = []
bg_durations = []

# 遍历 GIF 的所有帧并缓存为 Pygame Surface
for frame in range(bg_gif_image.n_frames):
    bg_gif_image.seek(frame)
    frame_surface = pygame.image.fromstring(
        bg_gif_image.convert("RGB").tobytes(),
        bg_gif_image.size,
        "RGB"
    )
    scaled_frame = pygame.transform.scale(frame_surface, (SCREEN_WIDTH, SCREEN_HEIGHT))  # 缩放到窗口大小
    bg_frames.append(scaled_frame)
    bg_durations.append(bg_gif_image.info.get("duration", 100))  # 每帧持续时间（默认 100 毫秒）

bg_index = 0
bg_timer = pygame.time.get_ticks()

current_bg_frame = bg_frames[0]  # 初始化为第一帧

# 加载并缩放按钮图片
button_images = [
    pygame.image.load("./png/1.png"),
    pygame.image.load("./png/2.png"),
    pygame.image.load("./png/3.png")
]

# 按钮缩放比例（根据窗口大小调整按钮尺寸比例）
button_width = int(SCREEN_WIDTH * 0.11)  # 按钮宽度为窗口宽度的 10%
button_height = int(SCREEN_HEIGHT * 0.23)  # 按钮高度为窗口高度的 10%

button_images = [pygame.transform.scale(img, (button_width, button_height)) for img in button_images]
button_hover_images = [pygame.transform.scale(img, (int(button_width * 1.1), int(button_height * 1.1))) for img in button_images]

# 动态计算按钮位置（整体向左移 50 像素，向下移 20 像素）
button_spacing = int(SCREEN_WIDTH * 0.03)  # 按钮之间的间距
button_positions = [
    (SCREEN_WIDTH // 2 - button_width - button_spacing -150, SCREEN_HEIGHT // 2 + 60),
    (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 60),
    (SCREEN_WIDTH // 2 + button_width + button_spacing -150, SCREEN_HEIGHT // 2 + 60)
]
# 初始化按钮的矩形区域
button_rects = [
    pygame.Rect(pos[0], pos[1], button_width, button_height)
    for pos in button_positions
]



# 占卜页面变量
text_question = ""
text_numbers = ""
response_text = "请在上方输入问题和三个三位数数字"
input_active_question = False
input_active_numbers = False
response_ready = True

# 初始化时钟
clock = pygame.time.Clock()

# 音乐设置
pygame.mixer.init()  # 初始化混音器
pygame.mixer.music.load("./audio/bg.mp3")  # 加载背景音乐
pygame.mixer.music.set_volume(0.6)  # 设置音量为 60%
pygame.mixer.music.play(-1, 0.0)  # 循环播放 (-1 表示无限循环)

# 主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if current_page == "main":
            text_question = ""
            text_numbers = ""
            if event.type == pygame.MOUSEBUTTONDOWN:
                for i, rect in enumerate(button_rects):
                    if rect.collidepoint(event.pos):  # 检测点击是否在矩形区域内
                        if i == 0:
                            current_page = "draw"
                        elif i == 1:
                            current_page = "divination"
                        elif i == 2:
                            current_page = "calm"


        elif current_page == "divination":
            # 调用占卜页面事件处理函数
            (
                text_question,
                text_numbers,
                input_active_question,
                input_active_numbers,
                #response_ready,
            ) = handle_divination_events(
                event,
                text_question,
                text_numbers,
                input_active_question,
                input_active_numbers,
                #response_ready,
                ask_openai_api,
                lambda response: globals().update({"response_text": response}),
            )
            result = handle_return_events(event)
            # 如果返回状态是 "main"，切换回主页面
            if result == "main":
                current_page = "main"
        elif current_page == "draw":
            # 更新抽签页面的状态
            result = handle_draw_events(event)
            # 如果返回状态是 "main"，切换回主页面
            if result == "main":
                current_page = "main"
        elif current_page == "calm":
            result = handle_calm_events(event)  # 调用静心页面的事件处理函数
            if result == "main":
                current_page = "main"

    # 绘制页面
    # 更新背景帧
    if current_page == "main":

        # 绘制主页面
        current_time = pygame.time.get_ticks()
        if current_time - bg_timer >= bg_durations[bg_index]:
            bg_index = (bg_index + 1) % len(bg_frames)  # 循环播放
            bg_timer = current_time

        # 绘制当前帧到屏幕
        screen.blit(bg_frames[bg_index], (0, 0))
        # 获取鼠标位置
        mouse_pos = pygame.mouse.get_pos()

        # 绘制按钮
        for i, (img, hover_img, rect) in enumerate(zip(button_images, button_hover_images, button_rects)):
            if rect.collidepoint(mouse_pos):  # 检测鼠标悬停
                # 绘制放大效果的按钮
                hover_offset_x = (hover_img.get_width() - img.get_width()) // 2
                hover_offset_y = (hover_img.get_height() - img.get_height()) // 2
                screen.blit(hover_img, (rect.x - hover_offset_x, rect.y - hover_offset_y))
            else:
                # 绘制普通按钮
                screen.blit(img, rect.topleft)

    elif current_page == "divination":
        # 绘制占卜页面
        draw_divination_page(
            screen,
            font,
            text_question,
            text_numbers,
            response_text,
            input_active_question,
            input_active_numbers,
            response_ready,
        )
    elif current_page == "draw":
        # 绘制抽签页面
        draw_draw_page(screen)
    elif current_page == "calm":
        # 绘制抽签页面
        draw_calm_page(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
