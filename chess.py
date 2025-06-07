from enum import Enum

class PieceType(Enum):
    KING = "king"      # 王
    QUEEN = "queen"    # 后
    ROOK = "rook"      # 车
    BISHOP = "bishop"  # 象
    KNIGHT = "knight"  # 马
    PAWN = "pawn"      # 兵

class PieceColor(Enum):
    WHITE = "white"    # 白方
    BLACK = "black"    # 黑方
    NONE = "none"      # 无方
class ChessPiece:
    # 修正：保留一个__init__方法，通过参数初始化颜色和类型
    def __init__(self, color: PieceColor, piece_type: PieceType):
        self.color = color    # 棋子颜色（白/黑）
        self.type = piece_type  # 棋子类型（王/后/车/象/马/兵）
    
    # （可选）若需要通过整数初始化，可添加类方法（如from_int）
    @classmethod
    def from_int(chess, num: int):
        color = PieceColor.BLACK if num <= 6 else PieceColor.WHITE
        num = num if num <= 6 else num - 6
        piece_type_map = {
            1: PieceType.BISHOP,
            2: PieceType.KING,
            3: PieceType.KNIGHT,
            4: PieceType.PAWN,
            5: PieceType.QUEEN,
            6: PieceType.ROOK
        }
        return chess(color, piece_type_map.get(num, None))

    def __repr__(self):
        return f"{self.color.value[0].upper()}{self.type.value[0].upper()}"  # 简化表示（如 "WK" 代表白王）

class ChessBoard:
    def __init__(self):
        # 初始化8x8棋盘（行0-7，列0-7，对应国际象棋坐标a1-h8）
        self.board: list[list[ChessPiece | None]] = [[None for _ in range(8)] for _ in range(8)]
        self._initialize_board()  # 调用初始化方法设置初始棋子位置

    def _initialize_board(self):
        """初始化棋盘的初始布局（按国际象棋规则）"""
    def set_piece(self, row: int, col: int, cls: int):
        """设置指定位置的棋子（行/列索引0-7）"""
        piece = ChessPiece.from_int(cls) 
        if 0 <= row < 8 and 0 <= col < 8:
            self.board[row][col] = piece

    def get_piece(self, row: int, col: int) -> ChessPiece | None:
        """获取指定位置的棋子（行/列索引0-7）"""
        if 0 <= row < 8 and 0 <= col < 8:
            return self.board[row][col]
        return None

    def move_piece(self, from_row: int, from_col: int, to_row: int, to_col: int) -> bool:
        """移动棋子（简化逻辑，未包含规则校验）"""
        source_piece = self.get_piece(from_row, from_col)
        target_piece = self.get_piece(to_row, to_col)
        
        if not source_piece:
            return False  # 源位置无棋子
        
        # 移动棋子（实际需添加规则校验，如颜色轮动、走法合法性等）
        self.board[to_row][to_col] = source_piece
        self.board[from_row][from_col] = None
        return True

    def __repr__(self):
        """打印棋盘状态（简化显示）"""
        board_str = "   a  b  c  d  e  f  g  h\n"
        for row in range(8):
            board_str += f"{8 - row} "  # 行号（8-1）
            for col in range(8):
                piece = self.board[row][col]
                board_str += f" {piece if piece else '  '} "
            board_str += f" {8 - row}\n"
        board_str += "   a  b  c  d  e  f  g  h"
        return board_str

# 使用示例
if __name__ == "__main__":
    # 创建棋盘实例
    chessboard = ChessBoard()
    # 打印初始棋盘状态
    print("初始棋盘状态：")
    print(chessboard)
    
    # 示例：移动白方a2兵到a3（行1列0 -> 行2列0）
    chessboard.move_piece(1, 0, 2, 0)
    print("\n移动后a2兵到a3的棋盘状态：")
    print(chessboard)