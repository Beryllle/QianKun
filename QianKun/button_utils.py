import pygame

def draw_return_button(screen, base_image, hover_image, rect, mouse_pos):
    """
    绘制返回按钮，支持悬停放大效果。
    :param screen: Pygame 画布
    :param base_image: 普通状态图片
    :param hover_image: 悬停状态图片
    :param rect: 按钮矩形区域
    :param mouse_pos: 鼠标位置
    :return: 是否悬停
    """
    if rect.collidepoint(mouse_pos):  # 鼠标悬停
        offset_x = (hover_image.get_width() - base_image.get_width()) // 2
        offset_y = (hover_image.get_height() - base_image.get_height()) // 2
        screen.blit(hover_image, (rect.x - offset_x, rect.y - offset_y))
        return True
    else:
        screen.blit(base_image, rect.topleft)
        return False
