import pygame
import os
import random
from PIL import Image
from config import SCREEN_WIDTH, SCREEN_HEIGHT

# 初始化 pygame
pygame.init()

# 加载背景和 GIF 文件
bg_image = pygame.image.load("./bg/bg.jpg")
bg_image = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

bg2_image = pygame.image.load("./bg/bg2.jpg")
bg2_image = pygame.transform.scale(bg2_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

# 加载 draw.gif
draw_gif_image = Image.open("./gif/draw.gif")
draw_gif_frames = []
draw_gif_durations = []

for frame in range(draw_gif_image.n_frames):
    draw_gif_image.seek(frame)
    image = pygame.image.fromstring(draw_gif_image.tobytes(), draw_gif_image.size, draw_gif_image.mode)
    scaled_image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    draw_gif_frames.append(scaled_image)
    draw_gif_durations.append(draw_gif_image.info.get("duration", 100))

# 加载 draw2.gif
draw2_gif_image = Image.open("./gif/draw2.gif")
draw2_gif_frames = []
draw2_gif_durations = []

for frame in range(draw2_gif_image.n_frames):
    draw2_gif_image.seek(frame)
    image = pygame.image.fromstring(draw2_gif_image.tobytes(), draw2_gif_image.size, draw2_gif_image.mode)
    scaled_image = pygame.transform.scale(image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    draw2_gif_frames.append(scaled_image)
    draw2_gif_durations.append(draw2_gif_image.info.get("duration", 100))

# 加载按钮图片
start_draw_image = pygame.image.load("./png/start_draw.png")
start_draw_hover_image = pygame.transform.scale(
    start_draw_image, (int(start_draw_image.get_width() * 1.1), int(start_draw_image.get_height() * 1.1))
)

start_draw_width = SCREEN_WIDTH // 4.4
start_draw_height = SCREEN_HEIGHT // 5.2
start_draw_image = pygame.transform.scale(start_draw_image, (start_draw_width, start_draw_height))
start_draw_hover_image = pygame.transform.scale(start_draw_hover_image, (int(start_draw_width * 1.1), int(start_draw_height * 1.1)))
start_draw_rect = pygame.Rect(SCREEN_WIDTH // 2 - start_draw_width // 2, SCREEN_HEIGHT // 2 + 200, start_draw_width, start_draw_height)

re_draw_image = pygame.image.load("./png/re_draw.png")
re_draw_hover_image = pygame.transform.scale(
    re_draw_image, (int(re_draw_image.get_width() * 1.1), int(re_draw_image.get_height() * 1.1))
)

# 自适应屏幕的缩放比例
re_draw_width = SCREEN_WIDTH //4.4
re_draw_height = SCREEN_HEIGHT //5.2
re_draw_image = pygame.transform.scale(re_draw_image, (re_draw_width, re_draw_height))
re_draw_hover_image = pygame.transform.scale(re_draw_hover_image, (int(re_draw_width * 1.1), int(re_draw_height * 1.1)))
re_draw_rect = pygame.Rect(SCREEN_WIDTH // 2 - re_draw_width // 2, SCREEN_HEIGHT // 2 + 220, re_draw_width, re_draw_height)

# 加载返回按钮
back_image = pygame.image.load("./png/back.png")
back_hover_image = pygame.transform.scale(
    back_image, (int(back_image.get_width() * 1.1), int(back_image.get_height() * 1.1))
)
back_button_width = SCREEN_WIDTH // 11
back_button_height = SCREEN_HEIGHT // 10
back_image = pygame.transform.scale(back_image, (back_button_width, back_button_height))
back_hover_image = pygame.transform.scale(back_hover_image, (int(back_button_width * 1.1), int(back_button_height * 1.1)))
back_button_rect = pygame.Rect(20, 20, back_button_width, back_button_height)

# 加载音频文件并设置音量（最大音量为1.0）
pygame.mixer.init()  # 初始化音频混合器
draw_sound = pygame.mixer.Sound("./audio/draw.mp3")  # 加载音频
draw_sound.set_volume(0.8)

# 状态变量
current_background = "static"
draw_gif_index = 1  # 跳过第一帧
draw_gif_timer = 0
draw2_gif_index = 0
draw2_gif_timer = 0
lots_selected_image = None

# lots 文件夹路径
lots_folder = "./lots"

# 初始化时钟
clock = pygame.time.Clock()

# 主绘制函数
def draw_draw_page(screen):
    global current_background, draw_gif_index, draw_gif_timer, draw2_gif_index, draw2_gif_timer, lots_selected_image, draw_sound

    # 绘制背景
    if current_background == "static":
        screen.blit(bg_image, (0, 0))
    elif current_background == "draw_gif":
        if draw_gif_index == 1:  # 确保只在首次播放时播放音频
            draw_sound.play(-1)  # 循环播放音频
        current_time = pygame.time.get_ticks()
        if current_time - draw_gif_timer >= draw_gif_durations[draw_gif_index]:
            draw_gif_index += 1
            draw_gif_timer = current_time
        if draw_gif_index >= len(draw_gif_frames) - 1:  # 播放到倒数第二帧
            current_background = "draw2_gif"
            draw2_gif_index = 1
            draw2_gif_timer = pygame.time.get_ticks()
            draw_sound.stop()  # 停止音频播放，切换到下一动画
        else:
            screen.blit(draw_gif_frames[draw_gif_index], (0, 0))
    elif current_background == "draw2_gif":
        current_time = pygame.time.get_ticks()
        # 从第二帧开始到倒数第二帧循环播放
        if current_time - draw2_gif_timer >= draw2_gif_durations[draw2_gif_index]:
            draw2_gif_index += 1
            if draw2_gif_index >= len(draw2_gif_frames) - 1:  # 限制到倒数第二帧
                draw2_gif_index = 1  # 回到第二帧
            draw2_gif_timer = current_time
        screen.blit(draw2_gif_frames[draw2_gif_index], (0, 0))
    elif current_background == "lots":
        screen.blit(bg2_image, (0, 0))
        if lots_selected_image:
            scaled_width = SCREEN_WIDTH // 1.5
            scaled_height = SCREEN_HEIGHT // 1.5
            scaled_lots_image = pygame.transform.scale(lots_selected_image, (scaled_width, scaled_height))
            # 将随机图片绘制在屏幕中央
            lots_rect = scaled_lots_image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(scaled_lots_image, lots_rect.topleft)
            # 绘制重新开始按钮
            mouse_pos = pygame.mouse.get_pos()
            if re_draw_rect.collidepoint(mouse_pos):
                screen.blit(re_draw_hover_image, re_draw_rect.topleft)
            else:
                screen.blit(re_draw_image, re_draw_rect.topleft)

    # 绘制按钮
    mouse_pos = pygame.mouse.get_pos()

    if current_background == "static":
        if start_draw_rect.collidepoint(mouse_pos):
            screen.blit(start_draw_hover_image, start_draw_rect.topleft)
        else:
            screen.blit(start_draw_image, start_draw_rect.topleft)
    elif current_background == "lots" and lots_selected_image:
        if re_draw_rect.collidepoint(mouse_pos):
            screen.blit(re_draw_hover_image, re_draw_rect.topleft)
        else:
            screen.blit(re_draw_image, re_draw_rect.topleft)

    # 返回按钮
    if back_button_rect.collidepoint(mouse_pos):
        screen.blit(back_hover_image, back_button_rect.topleft)
    else:
        screen.blit(back_image, back_button_rect.topleft)

def reset_draw_page():
    global current_background, draw_gif_index, draw_gif_timer, draw2_gif_index, draw2_gif_timer, lots_selected_image
    current_background = "static"
    draw_gif_index = 1  # 重置为从第一帧开始
    draw_gif_timer = 0
    draw2_gif_index = 0  # 重置 draw2.gif 的帧索引
    draw2_gif_timer = 0
    lots_selected_image = None  # 清空抽签图片
    draw_sound.stop()

# 主事件处理函数
def handle_draw_events(event):
    global current_background, draw_gif_index, draw_gif_timer, lots_selected_image

    if event.type == pygame.MOUSEBUTTONDOWN:
        if back_button_rect.collidepoint(event.pos):
            reset_draw_page()  # 重置页面状态
            return "main"
        elif current_background == "static" and start_draw_rect.collidepoint(event.pos):
            current_background = "draw_gif"
            draw_gif_index = 1
            draw_gif_timer = pygame.time.get_ticks()
        elif current_background == "lots" and re_draw_rect.collidepoint(event.pos):
            current_background = "static"
            lots_selected_image = None
        elif current_background == "draw2_gif":  # 点击 draw2.gif 切换到 lots
            current_background = "lots"
            lots_selected_image = get_random_lots_image()

# 随机抽签图片函数
def get_random_lots_image():
    files = [f for f in os.listdir(lots_folder) if f.endswith(".jpg")]
    if not files:
        return None
    selected_file = random.choice(files)
    return pygame.image.load(os.path.join(lots_folder, selected_file))

# 主程序循环结束后
pygame.quit()
