import pygame
from PIL import Image
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FONT_PATH, BLACK
from button_utils import draw_return_button

# 加载 GIF 并提取帧
def load_gif_frames(file_path, target_width, speed_factor=1):
    gif_image = Image.open(file_path)
    frames = []
    durations = []
    for frame in range(gif_image.n_frames):
        gif_image.seek(frame)
        image = pygame.image.fromstring(gif_image.tobytes(), gif_image.size, gif_image.mode)
        scale_factor = target_width / gif_image.width
        scaled_size = (int(gif_image.width * scale_factor), int(gif_image.height * scale_factor))
        scaled_image = pygame.transform.scale(image, scaled_size)
        frames.append(scaled_image)
        # 调整帧持续时间
        original_duration = gif_image.info.get("duration", 100)
        adjusted_duration = int(original_duration * speed_factor)
        durations.append(adjusted_duration)
    return frames, durations

# 动图缩放宽度为屏幕的 25%
scaled_width = SCREEN_WIDTH // 3

# 加载右侧 GIF 动画
right_gif_frames, right_gif_durations = load_gif_frames("./gif/muyu.gif", scaled_width)

# 状态变量
right_cached_frames = right_gif_frames[:]  # 缓存所有帧
right_gif_playing = False
right_gif_index = 1  # 从第二帧开始
right_gif_timer = 0
right_click_count = 0  # 右侧点击计数

# 加载背景 GIF 动画
xiang_gif_frames, xiang_gif_durations = load_gif_frames("./gif/xiang.gif", SCREEN_WIDTH, speed_factor=2)

# 状态变量
xiang_gif_index = 1  # 从第二帧开始播放
xiang_gif_timer = 0
xiang_gif_finished = False

# 加载右侧播放按钮图片
merit_button_image = pygame.image.load("./png/merit.png")
merit_button_hover_image = pygame.transform.scale(
    merit_button_image, (int(merit_button_image.get_width() * 1.1), int(merit_button_image.get_height() * 1.1))
)

# 自适应屏幕的缩放比例
merit_button_width = SCREEN_WIDTH //4.4
merit_button_height = SCREEN_HEIGHT //5.2
merit_button_image = pygame.transform.scale(merit_button_image, (merit_button_width, merit_button_height))
merit_button_hover_image = pygame.transform.scale(
    merit_button_hover_image, (int(merit_button_width * 1.1), int(merit_button_height * 1.1))
)

# 创建按钮矩形
merit_button_rect = pygame.Rect(
    SCREEN_WIDTH - scaled_width - 50, SCREEN_HEIGHT // 2, merit_button_width, merit_button_height
)

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

# 初始化音频
pygame.mixer.init()  # 初始化音频混合器
muyu_sound = pygame.mixer.Sound("./audio/muyu.mp3")  # 加载音频文件
muyu_sound.set_volume(1.0)  # 设置音量为最大（最大值为 1.0）

def draw_calm_page(screen):
    """绘制静心页面"""
    global xiang_gif_index, xiang_gif_timer, xiang_gif_finished
    global right_gif_playing, right_gif_index, right_gif_timer, right_click_count


    # 绘制背景 GIF 动画
    if not xiang_gif_finished:
        current_time = pygame.time.get_ticks()
        if current_time - xiang_gif_timer >= xiang_gif_durations[xiang_gif_index]:
            xiang_gif_index += 1
            xiang_gif_timer = current_time
        if xiang_gif_index >= len(xiang_gif_frames) - 1:  # 停止在倒数第二帧
            xiang_gif_index = len(xiang_gif_frames) - 2
            xiang_gif_finished = True
    # 绘制当前帧
    screen.blit(xiang_gif_frames[xiang_gif_index], (0, 0))

    # 显示右侧 GIF 动画
    right_frame = right_cached_frames[right_gif_index]
    right_rect = right_frame.get_rect(right=SCREEN_WIDTH - 100, centery=SCREEN_HEIGHT // 2 + 50)
    screen.blit(right_frame, right_rect.topleft)

    if right_gif_playing:
        current_time = pygame.time.get_ticks()
        if current_time - right_gif_timer >= right_gif_durations[right_gif_index]:
            right_gif_index += 1
            right_gif_timer = current_time
        if right_gif_index >= len(right_cached_frames):  # 播放完成
            right_gif_playing = False
            right_gif_index = 1  # 重置为初始帧

    # 右侧点击计数显示
    font = pygame.font.Font(FONT_PATH, 28)
    click_count_text = font.render(f"功德次数(Merit Number): {right_click_count}", True, BLACK)
    click_count_rect = click_count_text.get_rect(centerx=right_rect.centerx, bottom=right_rect.top - 10)
    screen.blit(click_count_text, click_count_rect)

    # 绘制右侧播放按钮
    merit_button_rect.top = right_rect.bottom
    mouse_pos = pygame.mouse.get_pos()
    if merit_button_rect.collidepoint(mouse_pos):
        screen.blit(merit_button_hover_image, merit_button_rect.topleft)
    else:
        screen.blit(merit_button_image, merit_button_rect.topleft)

    # 提示文字
    font = pygame.font.Font(FONT_PATH, 32)
    hint_text_cn = font.render("请耐心等待香火燃尽", True, BLACK)
    hint_text_en = font.render("Please wait patiently for the incense to burn out", True, BLACK)
    hint_rect_cn = hint_text_cn.get_rect(center=(SCREEN_WIDTH // 2, 50))
    screen.blit(hint_text_cn, hint_rect_cn)
    hint_rect_en = hint_text_en.get_rect(center=(SCREEN_WIDTH // 2, 90))
    screen.blit(hint_text_en, hint_rect_en)

    # 返回按钮2
    draw_return_button(screen, back_image, back_hover_image, back_button_rect, mouse_pos)

def reset_calm_page():
    global xiang_gif_index, xiang_gif_timer, xiang_gif_finished
    global right_gif_playing, right_gif_index, right_gif_timer, right_click_count

    xiang_gif_index = 1
    xiang_gif_timer = 0
    xiang_gif_finished = False
    right_gif_playing = False
    right_gif_index = 1
    right_gif_timer = 0
    right_click_count = 0

def handle_calm_events(event):
    """处理静心页面事件"""
    global xiang_gif_finished, right_gif_playing, right_gif_index, right_gif_timer, right_click_count

    # 定义按钮位置
    if event.type == pygame.MOUSEBUTTONDOWN:
        if back_button_rect.collidepoint(event.pos) and xiang_gif_finished:
            reset_calm_page()  # 重置页面状态
            return "main"  # 返回主页面
        elif merit_button_rect.collidepoint(event.pos):
            muyu_sound.play()
            # 点击右侧按钮播放 GIF
            right_gif_playing = True
            right_gif_index = 1
            right_gif_timer = pygame.time.get_ticks()
            right_click_count += 1

    return None
