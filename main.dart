// 文件路径：lib/main.dart
import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:camera/camera.dart';
import 'package:image_picker/image_picker.dart'; // 替代 image 包import 'package:tflite_flutter/tflite_flutter.dart';
import 'package:path_provider/path_provider.dart';
import 'package:image/image.dart' as img;
import 'package:tflite_flutter/tflite_flutter.dart' as tfl;
// import 'package:opencv/opencv.dart';
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final cameras = await availableCameras();
  runApp(ChessVisionApp(camera: cameras.first));
}

class ChessVisionApp extends StatelessWidget {
  final CameraDescription camera;
  const ChessVisionApp({Key? key, required this.camera}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: CameraView(camera: camera),
    );
  }
}

class CameraView extends StatefulWidget {
  final CameraDescription camera;
  const CameraView({Key? key, required this.camera}) : super(key: key);

  @override
  _CameraViewState createState() => _CameraViewState();
}

class _CameraViewState extends State<CameraView> {
  late CameraController _controller;
  List<ChessPiece> _detectedPieces = []; // 模拟识别结果
  bool _showGrid = true;
  bool _isDetecting = false;
  DateTime? _lastDetectionTime;
  bool _autoDetection = false;  // 自动检测开关 
  String _detectionStatus = '';
  tfl.Interpreter? _interpreter; // 替换 YoloModel
  bool _isModelLoaded = false;

  @override
  void initState() {
    super.initState();
    _initializeCamera();
    //_mockDetection(); // 模拟识别数据
    _loadModel(); // 加载模型
  }

  Future<void> _loadModel() async {
    try {
      _interpreter = await tfl.Interpreter.fromAsset('assets/models/best_float16.tflite');
      print('模型加载成功');
      setState(() {
        _isModelLoaded = true;
        _detectionStatus = '模型已加载';
      });
    } catch (e) {
      print('模型加载失败: $e');
      setState(() => _detectionStatus = '模型加载失败: ${e.toString()}');
    }
  }
  Future<void> _initializeCamera() async {
    _controller = CameraController(
      widget.camera,
      ResolutionPreset.high,
    );
    await _controller.initialize();
    if (!mounted) return;
    setState(() {});
  }

  // 模拟识别结果（后续替换为实际算法接口）
  void _mockDetection() {
    _detectedPieces = [
      ChessPiece(type: 'K', color: 'white', x: 2, y: 3), // 王
      ChessPiece(type: 'Q', color: 'black', x: 7, y: 4), // 后
      ChessPiece(type: 'R', color: 'white', x: 1, y: 1), // 车
      ChessPiece(type: 'B', color: 'black', x: 3, y: 5), // 象
      ChessPiece(type: 'N', color: 'white', x: 6, y: 7), // 马
      ChessPiece(type: 'P', color: 'black', x: 5, y: 6), // 兵
    ];
  }

  @override
  Widget build(BuildContext context) {
    if (!_controller.value.isInitialized) {
      return Container(color: Colors.black);
    }
    return Scaffold(
      appBar: AppBar(
        title: Text('棋盘识别'),
        actions: [
          IconButton(
            icon: Icon(_showGrid ? Icons.grid_on : Icons.grid_off),
            onPressed: () => setState(() => _showGrid = !_showGrid),
          ),
          // 自动检测开关
          Switch(
            value: _autoDetection,
            onChanged: (value) => setState(() => _autoDetection = value),
          ),
        ],
      ),
      body: Stack(
        children: [
          CameraPreview(_controller),
          if (_showGrid)
            CustomPaint(
              painter: ChessBoardPainter(pieces: _detectedPieces),
              size: Size.infinite,
            ),
          if (_isDetecting)
            Center(
              child: CircularProgressIndicator(),
            ),

          Positioned(
            bottom: 20,
            left: 20,
            child: Text(
              _detectionStatus,
              style: TextStyle(
                color: Colors.white,
                fontSize: 16,
                backgroundColor: Colors.black54,
              ),
            ),
          ),

          if (_lastDetectionTime != null)
            Positioned(
              bottom: 20,
              right: 20,
              child: Text(
                '上次检测: ${_lastDetectionTime!.toString().substring(11, 19)}',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  backgroundColor: Colors.black54,
                ),
              ),
            ),

        ],
      ),
      floatingActionButton: Column(
        mainAxisAlignment: MainAxisAlignment.end,
        children: [
          // 手动检测按钮
          FloatingActionButton(
            onPressed: _isDetecting ? null : _captureAndDetect,
            tooltip: '识别棋盘',
            heroTag: 'detectButton',
            child: Icon(Icons.camera),
          ),
          SizedBox(height: 10),
          // 模拟检测按钮
          FloatingActionButton(
            onPressed: _mockDetection,
            heroTag: 'mockButton',
            child: Icon(Icons.autorenew),
          ),
        ],
      ),
      // floatingActionButton: FloatingActionButton(
      //   onPressed: () => _mockDetection(), // 测试用
      //   child: Icon(Icons.camera),
      // ),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    _interpreter?.close(); // 添加这行
    super.dispose();
  }

  Future<void> _captureAndDetect() async {
    if (!_controller.value.isInitialized || !_isModelLoaded) return;
    
    setState((){
      _isDetecting = true;
      _detectionStatus = '检测中...';
    });
    
    try {
      // 1. 捕获当前帧
      final image = await _controller.takePicture();
      
      // 2. 调用棋盘检测算法
      final boardState = await _detectChessBoard(image.path);
      
      // 3. 更新UI状态
      setState(() {
        _detectedPieces = boardState;
        _lastDetectionTime = DateTime.now();
        _detectionStatus = '检测成功: ${_lastDetectionTime!.toString().substring(11, 19)}';
      });
    } catch (e) {
      print('Detection error: $e');
      setState(() => _detectionStatus = '错误: ${e.toString()}');
    } finally {
      setState(() => _isDetecting = false);
    }
  }

  Future<List<ChessPiece>> _detectChessBoard(String imagePath) async {
    if (!_isModelLoaded) return [];
    
    setState(() => _isDetecting = true);
    
    try {
      // 1. 读取图像
      final imageBytes = await File(imagePath).readAsBytes();
      final originalImage = img.decodeImage(imageBytes);
      
      if (originalImage == null) throw Exception('图像解码失败');
      
      // 2. 调整大小为YOLO输入尺寸 (640x640)
      final resizedImage = img.copyResize(
        originalImage,
        width: 640,
        height: 640,
      );
      
      // 3. 转换图像为模型输入格式
      final inputBuffer = Float32List(1 * 640 * 640 * 3);
      int pixelIndex = 0;
      
      for (int y = 0; y < 640; y++) {
        for (int x = 0; x < 640; x++) {
          final pixel = resizedImage.getPixel(x, y);
          final a = (pixel >> 24) & 0xFF;
          final r = (pixel >> 16) & 0xFF;
          final g = (pixel >> 8) & 0xFF;
          final b = pixel & 0xFF;
          
          // 归一化并填充缓冲区 (忽略alpha通道)
          inputBuffer[pixelIndex++] = r / 255.0;
          inputBuffer[pixelIndex++] = g / 255.0;
          inputBuffer[pixelIndex++] = b / 255.0;
        }
      }

      // 4. 执行推理
      // 获取模型输出张量形状
      final outputTensor = _interpreter!.getOutputTensor(0);
      final outputShape = outputTensor.shape;
      final outputSize = outputShape.reduce((a, b) => a * b);
      
      // 创建输出缓冲区 - 使用Float32List而不是List<dynamic>
      final outputBuffer = Float32List(outputSize);
      
      // 运行推理 - 使用正确的输入/输出类型
      _interpreter!.run(
        [inputBuffer], // 输入作为列表
        [outputBuffer]  // 输出作为列表
      );
      
      // 5. 解析检测结果
      final detections = _parseYoloOutput(
        outputBuffer, 
        outputShape: outputShape,
        confidenceThreshold: 0.5
      );
      
      return detections.map((det) {
        return ChessPiece(
          type: _classIdToPieceType(det.classId),
          color: det.classId < 6 ? 'white' : 'black',
          x: det.x, 
          y: det.y,
        );
      }).toList();
    } catch (e) {
      print('检测错误: $e');
      return [];
    } finally {
      setState(() => _isDetecting = false);
    }
  }

  // 解析函数保持不变
  List<Detection> _parseYoloOutput(
    Float32List outputBuffer,
    {
    required List<int> outputShape,
    required double confidenceThreshold,
  }) {
    final detections = <Detection>[];
    final gridSize = 640;
    
    // 解析输出形状 [batch, num_detections, detection_size]
    final batchSize = outputShape[0];
    final numDetections = outputShape[1];
    final detectionSize = outputShape[2];
    
    // 确保检测尺寸至少为85 (x, y, w, h, conf + 80 classes)
    if (detectionSize < 85) {
      print('警告: 检测尺寸小于85 ($detectionSize)，可能无法正确解析');
      return detections;
    }
    
    int index = 0;
    for (int b = 0; b < batchSize; b++) {
      for (int i = 0; i < numDetections; i++) {
        // 计算当前检测在缓冲区中的起始位置
        final startIndex = b * numDetections * detectionSize + i * detectionSize;
        
        // 提取边界框坐标和置信度
        final cx = outputBuffer[startIndex];
        final cy = outputBuffer[startIndex + 1];
        final width = outputBuffer[startIndex + 2];
        final height = outputBuffer[startIndex + 3];
        final confidence = outputBuffer[startIndex + 4];
        
        if (confidence < confidenceThreshold) continue;
        
        // 找到最大概率的类别
        double maxProb = 0;
        int classId = 0;
        for (int c = 0; c < 12; c++) { // 12类棋子 (6白棋+6黑棋)
          final prob = outputBuffer[startIndex + 5 + c];
          if (prob > maxProb) {
            maxProb = prob;
            classId = c;
          }
        }
        
        // 转换为归一化坐标 [0-1]
        final x = (cx - width / 2) / gridSize;
        final y = (cy - height / 2) / gridSize;
        
        detections.add(Detection(
          classId: classId,
          confidence: confidence,
          x: x,
          y: y,
        ));
      }
    }
    
    // 按置信度排序
    detections.sort((a, b) => b.confidence.compareTo(a.confidence));
    return detections;
  }
  
}

// 添加 Detection 数据类
  class Detection {
    final int classId;
    final double confidence;
    final double x;
    final double y;

    Detection({
      required this.classId,
      required this.confidence,
      required this.x,
      required this.y,
    });
  }

  // 类别ID映射到棋子类型
  String _classIdToPieceType(int classId) {
    const types = ['K', 'Q', 'R', 'B', 'N', 'P'];
    return types[classId % 6];
  }

// 棋子数据模型
class ChessPiece {
  final String type;
  final String color;
  final double x; // 相对坐标 [0-1]
  final double y;

  ChessPiece({
    required this.type,
    required this.color,
    required this.x,
    required this.y,
  });
}

// 棋盘绘制层
class ChessBoardPainter extends CustomPainter {
  final List<ChessPiece> pieces;
  ChessBoardPainter({required this.pieces});

  @override
  void paint(Canvas canvas, Size size) {
    // 1. 计算正方形棋盘区域（居中）
    final boardSize = size.width > size.height 
        ? size.height * 0.9 // 竖屏模式：高度90%
        : size.width * 0.9; // 横屏模式：宽度90%
    final boardLeft = (size.width - boardSize) / 2;
    final boardTop = (size.height - boardSize) / 2;
    // final boardRect = Rect.fromLTWH(boardLeft, boardTop, boardSize, boardSize);

    final gridPaint  = Paint()
      ..color = Colors.blue.withOpacity(0.3)
      ..strokeWidth = 1.5
      ..style = PaintingStyle.stroke;


    // 绘制棋盘网格（简化为8x8）
    final cellSize = boardSize / 8;
    for (int i = 0; i <= 8; i++) {
      final yPos = boardTop + i * cellSize;
      canvas.drawLine(Offset(boardLeft, yPos), Offset(boardLeft + boardSize, yPos), gridPaint);
      
      final xPos = boardLeft + i * cellSize;
      canvas.drawLine(Offset(xPos, boardTop), Offset(xPos, boardTop + boardSize), gridPaint);
    }

    // 绘制棋子 - 修复字母显示问题
    final textStyle = TextStyle(
      fontSize: cellSize * 0.3, // 增大字体大小
      fontWeight: FontWeight.bold,
      height: 1.0, // 确保行高为1.0
    );

    // 绘制检测到的棋子
    for (final piece in pieces) {
      final col = (piece.x - 1).toInt();
      final row = (piece.y - 1).toInt(); // 注意：这里假设棋盘坐标从1开始

      // 计算网格中心坐标，没问题
      final posX = boardLeft + (col + 0.5) * cellSize;
      final posY = boardTop + (row + 0.5) * cellSize;
      // 棋子半径（基于格子大小）
      final radius = cellSize * 0.4;
    // 棋子外圈
      canvas.drawCircle(
        Offset(posX, posY),
        radius,
        Paint()
          ..color = piece.color == 'white' ? Colors.white : Colors.black
          ..style = PaintingStyle.fill,
      );
      
      // 棋子内圈
      final innerColor = piece.color == 'white' ? Colors.black : Colors.white;
      canvas.drawCircle(
        Offset(posX, posY),
        radius * 0.85,
        Paint()
          ..color = innerColor
          ..style = PaintingStyle.stroke
          ..strokeWidth = 2,
      );

      // 添加棋子字母 - 新增部分
      final text = piece.type.length > 1 ? piece.type[0] : piece.type;
      final textSpan = TextSpan(
        text: text,
        style: textStyle.copyWith(
          color: innerColor, // 使用与内圈相同的颜色
          shadows: [
            Shadow(
              blurRadius: 1,
              color: piece.color == 'white' ? Colors.white : Colors.black,
              offset: Offset(0, 0),
            ),
          ],
        ),
      );
      
      final textPainter = TextPainter(
        text: textSpan,
        textDirection: TextDirection.ltr,
        textAlign: TextAlign.center,
      )..layout(minWidth: 0, maxWidth: size.width);
      
      // 计算文本位置使其居中
      final textX = posX - textPainter.width / 2;
      final textY = posY - textPainter.height / 2;
      
      textPainter.paint(canvas, Offset(textX, textY));
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}