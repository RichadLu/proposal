
这个项目属于中国海洋大学计算机学院计算机视觉课程期末项目

## 视频链接
- https://www.bilibili.com/video/BV1tcKpzkEyY/

## 项目成员
刘翔宇
刘成喜
于铭洋
杨子凡
欧如根

## 主题
**国际象棋的计算机视觉应用**

## 主要功能
- 识别棋盘 
- 识别棋盘上的棋子 
- 判断每个棋子在棋盘的哪个格子里
- gui可视化显示，APP
## 文件用途说明
- best.pt yolo11训练后的权重文件
- chess.py 定义储存棋局状态的数据类型
- getchess.py 封装get_chess_info函数，调用yolo11检测棋子，并返回棋子位置
- getcorners.py 使用传统计算机视觉方法检测棋盘，返回棋盘的四个角的位置，方便计算透视矩阵
- getresult.py 执行此文件得到棋局状态
- gui.py 执行此文件通过前端检测棋局状态
- report.pdf 使用latex编写的实验报告
  

