import cv2
import numpy as np
from getcorners import getcorners
from getchess import get_chess_info
from chess import ChessBoard, ChessPiece, PieceColor, PieceType
def perspective_transform(img, src_pts, output_size=(800, 800)):
    """
    执行透视变换，将棋盘转换为顶视视角
    :param img: 原始图像
    :param src_pts: 原始图像中的四个角点（顺序：底左、底右、顶左、顶右）
    :param output_size: 输出图像尺寸（宽，高）
    :return: 变换后的图像
    """
    # 定义目标点（输出图像的四个角点，按对应顺序排列）
    dst_pts = np.float32([
        [0, output_size[1]],          # 底左（对应原图bl）
        [output_size[0], output_size[1]],  # 底右（对应原图br）
        [0, 0],                       # 顶左（对应原图tl）
        [output_size[0], 0]           # 顶右（对应原图tr）
    ])
    # 计算透视变换矩阵
    M = cv2.getPerspectiveTransform(src_pts, dst_pts)
    # 应用变换
    transformed_img = cv2.warpPerspective(img, M, output_size)
    return transformed_img

def save_chessboard_state(transformed_img, output_path="chessboard_state.txt"):
    """
    示例：将棋盘状态保存到txt文件（需根据实际棋子检测逻辑调整）
    :param transformed_img: 变换后的棋盘图像
    :param output_path: 输出文件路径
    """
    # 这里需要替换为实际的棋子检测逻辑（如通过颜色/轮廓检测棋子位置）
    # 示例逻辑：假设棋盘是8x8网格，每个格子状态为"空"或"有棋子"
    chessboard_state = [["空" for _ in range(8)] for _ in range(8)]
    
    # 保存到txt文件
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("棋盘状态（行x列）:\n")
        for row_idx, row in enumerate(chessboard_state):
            f.write(f"行{row_idx+1}: {','.join(row)}\n")
    print(f"棋盘状态已保存到：{output_path}")
def transform_single_point(point, output_size, M):
    """
    使用透视变换矩阵对单个点进行坐标变换
    :param point: 原始点坐标 (x, y)
    :param M: 透视变换矩阵（3x3）
    :return: 变换后的点坐标 (x', y')
    """
    # 将点转换为齐次坐标 [x, y, 1]
    point_homogeneous = np.array([[point]], dtype=np.float32)
    # 应用透视变换
    transformed_point = cv2.perspectiveTransform(point_homogeneous, M)
    # 提取坐标（去除多余维度）
    x, y = transformed_point[0][0]
    if x <0: x=0
    if y <0: y=0
    if x >output_size[0]: x=output_size[0]
    if y >output_size[1]: y=output_size[1]

    return (int(x), int(y))
def main(img_path):
    # 获取棋盘角点
    chessBoard = ChessBoard()
    corners = getcorners(img_path)
    chess_info_list = get_chess_info(img_path)
    print(chess_info_list)
    output_size=(800, 800)
    # 执行透视变换（假设输出尺寸为800x800）
    dst_pts = np.float32([
        [0, output_size[1]],          # 底左（对应原图bl）
        [output_size[0], output_size[1]],  # 底右（对应原图br）
        [0, 0],                       # 顶左（对应原图tl）
        [output_size[0], 0]           # 顶右（对应原图tr）
    ])
    M = cv2.getPerspectiveTransform(corners, dst_pts) 
    for chess_info in chess_info_list:
        x, y = chess_info["coordinates"]["x"], chess_info["coordinates"]["y"]
        transformed_point = transform_single_point((x, y),output_size,M)
        chessBoard.set_piece(transformed_point[1]//100,transformed_point[0]//100,chess_info["cls_id"])
       
    print("棋盘状态：")
    print(chessBoard)



if __name__ == "__main__":
    # 检测图像路径
    image_path = r"F:\jupyter notebook\CV\group\ultralytics-main\archive\Chess Pieces.yolov8-obb\test\images\cfc306bf86176b92ffc1afbb98d7896f_jpg.rf.effd71a5dcd98ec0f24072af5f7c0a31.jpg"
    main(image_path)
