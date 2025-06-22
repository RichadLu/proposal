import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw
import os
import cv2
import numpy as np

# 从您的项目文件中导入核心功能
from getcorners import getcorners
from getchess import get_chess_info
from chess import ChessBoard
from getresult import transform_single_point

class ChessVisionApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("国际象棋棋盘识别")
        self.geometry("1220x700")

        # --- 成员变量 ---
        self.image_path = None
        self.piece_images = {} # 用于存储棋子图片对象
        self.img_display_size = (600, 600)
        self.board_color1 = "#DDB88C" # 棋盘浅色
        self.board_color2 = "#A98867" # 棋盘深色

        # --- 加载资源 ---
        self.load_piece_images()

        # --- 创建UI组件 ---
        self.create_widgets()

    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 顶部按钮框架
        top_frame = ttk.Frame(main_frame)
        top_frame.pack(fill=tk.X, pady=5)

        self.upload_button = ttk.Button(top_frame, text="上传图片并开始检测", command=self.upload_and_process)
        self.upload_button.pack(side=tk.LEFT)

        self.status_label = ttk.Label(top_frame, text="请上传一张包含棋盘的图片。")
        self.status_label.pack(side=tk.LEFT, padx=10)

        # 图像显示框架
        image_frame = ttk.Frame(main_frame)
        image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        image_frame.columnconfigure(0, weight=1)
        image_frame.columnconfigure(1, weight=1)
        image_frame.rowconfigure(1, weight=1)

        ttk.Label(image_frame, text="原始图片", font=("Helvetica", 14, "bold")).grid(row=0, column=0, pady=5)
        ttk.Label(image_frame, text="识别结果", font=("Helvetica", 14, "bold")).grid(row=0, column=1, pady=5)

        # 用于显示图片的Label
        self.original_image_label = ttk.Label(image_frame, background="gray")
        self.original_image_label.grid(row=1, column=0, padx=5, sticky="nsew")

        self.result_image_label = ttk.Label(image_frame, background="gray")
        self.result_image_label.grid(row=1, column=1, padx=5, sticky="nsew")

    def load_piece_images(self):
        """加载所有棋子图片到内存中"""
        folder = "ComputerVision\BigHomework\proposal-main\piece_images"
        if not os.path.isdir(folder):
            messagebox.showerror("错误", f"找不到棋子图片文件夹 '{folder}'！\n请在项目根目录创建它，并放入12张棋子图片。")
            self.quit()
            return

        try:
            for piece_name in ["br", "bn", "bb", "bq", "bk", "bp", "wr", "wn", "wb", "wq", "wk", "wp"]:
                path = os.path.join(folder, f"{piece_name}.png")
                img = Image.open(path).convert("RGBA")
                self.piece_images[piece_name.upper()] = img
        except Exception as e:
            messagebox.showerror("图片加载错误", f"加载棋子图片时出错: {e}\n请确保所有12张PNG图片都存在且命名正确。")
            self.quit()

    def upload_and_process(self):
        """处理上传、检测和显示的全过程"""
        f_types = [("图片文件", "*.jpg;*.jpeg;*.png;*.bmp")]
        file_path = filedialog.askopenfilename(filetypes=f_types)

        if not file_path:
            return

        self.image_path = file_path
        self.status_label.config(text=f"正在处理: {os.path.basename(file_path)}...")
        self.update_idletasks() # 强制更新UI

        # 1. 显示原始图片
        try:
            original_pil_img = Image.open(self.image_path)
            original_pil_img.thumbnail(self.img_display_size)
            original_tk_img = ImageTk.PhotoImage(original_pil_img)
            self.original_image_label.config(image=original_tk_img)
            self.original_image_label.image = original_tk_img
        except Exception as e:
            messagebox.showerror("错误", f"无法打开或显示图片: {e}")
            self.status_label.config(text="图片处理失败。")
            return

        # 2. 运行后端检测逻辑
        try:
            # 获取棋盘角点
            corners = getcorners(self.image_path)
            if corners is None or len(corners) != 4:
                 raise ValueError("未能成功检测到棋盘的四个角点。")

            # 获取棋子信息
            chess_info_list = get_chess_info(self.image_path)

            # 创建棋盘对象并填充
            chess_board = self.reconstruct_board(corners, chess_info_list)

            # 3. 绘制并显示结果棋盘
            result_pil_img = self.draw_board_image(chess_board)
            result_pil_img.thumbnail(self.img_display_size)
            result_tk_img = ImageTk.PhotoImage(result_pil_img)
            self.result_image_label.config(image=result_tk_img)
            self.result_image_label.image = result_tk_img

            self.status_label.config(text="处理完成！")

        except Exception as e:
            messagebox.showerror("检测失败", f"处理过程中发生错误:\n{e}")
            self.status_label.config(text="检测失败，请重试。")
            # 清空结果图
            self.result_image_label.config(image='')
            self.result_image_label.image = None


    def reconstruct_board(self, corners, chess_info_list):
        """根据角点和棋子信息重建棋盘状态"""
        chess_board = ChessBoard()
        output_size = (800, 800) # 虚拟棋盘尺寸

        # 定义目标点
        dst_pts = np.float32([
            [0, output_size[1]],
            [output_size[0], output_size[1]],
            [0, 0],
            [output_size[0], 0]
        ])
        
        # 计算透视变换矩阵
        M = cv2.getPerspectiveTransform(corners, dst_pts)

        # 映射每个棋子到棋盘网格
        for chess_info in chess_info_list:
            x, y = chess_info["coordinates"]["x"], chess_info["coordinates"]["y"]
            transformed_point = transform_single_point((x, y), output_size, M)
            
            row = transformed_point[1] // 100
            col = transformed_point[0] // 100

            if 0 <= row < 8 and 0 <= col < 8:
                chess_board.set_piece(row, col, chess_info["cls_id"])
        
        return chess_board

    def draw_board_image(self, board_state: ChessBoard):
        """将ChessBoard对象绘制为PIL图像"""
        board_size = 800
        cell_size = board_size // 8
        board_img = Image.new("RGB", (board_size, board_size))
        draw = ImageDraw.Draw(board_img)

        for row in range(8):
            for col in range(8):
                color = self.board_color1 if (row + col) % 2 == 0 else self.board_color2
                draw.rectangle(
                    [(col * cell_size, row * cell_size), ((col + 1) * cell_size, (row + 1) * cell_size)],
                    fill=color
                )
        
        # 绘制棋子
        for r in range(8):
            for c in range(8):
                piece = board_state.get_piece(r, c)
                if piece:
                    piece_str = str(piece) # e.g., "WK", "BP"
                    piece_img = self.piece_images.get(piece_str)
                    if piece_img:
                        # 调整棋子图片大小并粘贴
                        piece_img_resized = piece_img.resize((int(cell_size*0.9), int(cell_size*0.9)), Image.Resampling.LANCZOS)
                        
                        # 计算粘贴位置（居中）
                        paste_x = c * cell_size + (cell_size - piece_img_resized.width) // 2
                        paste_y = r * cell_size + (cell_size - piece_img_resized.height) // 2
                        
                        board_img.paste(piece_img_resized, (paste_x, paste_y), piece_img_resized)

        return board_img


if __name__ == "__main__":
    app = ChessVisionApp()
    app.mainloop()
