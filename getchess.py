import warnings
warnings.filterwarnings('ignore')

from ultralytics import YOLO


def get_chess_info(img_path):
    """
    输入图片路径，返回检测到的棋子信息。
    
    返回值：列表，每个元素是包含 label, cls, conf, coordinates 的字典。
    """
    model = YOLO(r"F:\jupyter notebook\CV\group\ultralytics-main\runs\result\XSQ.2\weights\best.pt")
    results = model.predict(
        source=img_path,
        imgsz=640,
        save=True,  # 自动保存带框的图像
        conf=0.2,
        iou=0.7,
        show=False,  # 是否显示图像
    )

    chess_info_list = []

    for result in results:
        boxes = result.boxes  # Boxes 对象，包含所有检测框

        # 获取每个检测框的信息
        for i, box in enumerate(boxes):
            cls = int(box.cls.item())           # 类别索引
            label = result.names[cls]           # 类别名称
            conf = box.conf.item()              # 置信度
            xyxy = box.xyxy.tolist()[0]         # 检测框坐标 [x1, y1, x2, y2]

            # 将信息存储为字典并加入列表
            chess_info = {
                "label": label,
                "cls_id": cls,
                "confidence": round(conf, 2),
                "coordinates": {
                    "x": int((xyxy[0] * 0.2 + xyxy[2] * 0.8)),
                    "y": int((xyxy[1] * 0.2 + xyxy[3] * 0.8)),
                }
            }
            chess_info_list.append(chess_info)

    return chess_info_list


