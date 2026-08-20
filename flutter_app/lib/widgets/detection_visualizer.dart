import 'package:flutter/material.dart';
import '../../app/theme.dart';
import '../features/detection/detection_provider.dart';

class DetectionVisualizer extends StatelessWidget {
  final DetectionState state;

  const DetectionVisualizer({
    super.key,
    required this.state,
  });

  @override
  Widget build(BuildContext context) {
    return AspectRatio(
      aspectRatio: 3 / 4,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.black87,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: AppTheme.border, width: 2),
        ),
        child: Stack(
          children: [
            // Mock camera feed background
            Center(
              child: Icon(
                Icons.camera_alt_outlined,
                size: 64,
                color: Colors.white.withValues(alpha: 0.2),
              ),
            ),
            if (state.index >= DetectionState.plantDetected.index)
              _buildBoundingBox(
                context,
                rect: const Rect.fromLTRB(20, 40, 280, 360),
                label: 'PLANT',
                color: Colors.greenAccent,
              ),
            if (state.index >= DetectionState.leafDetected.index)
              _buildBoundingBox(
                context,
                rect: const Rect.fromLTRB(60, 100, 240, 300),
                label: 'LEAF',
                color: Colors.blueAccent,
              ),
            if (state.index >= DetectionState.diseaseDetected.index)
              _buildLesionMask(context),
            if (state.index >= DetectionState.targetReady.index)
              _buildTargetHighlight(context),
          ],
        ),
      ),
    );
  }

  Widget _buildBoundingBox(BuildContext context, {required Rect rect, required String label, required Color color}) {
    return Positioned.fromRect(
      rect: rect,
      child: Container(
        decoration: BoxDecoration(
          border: Border.all(color: color, width: 2),
        ),
        child: Align(
          alignment: Alignment.topLeft,
          child: Container(
            color: color,
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
            child: Text(
              label,
              style: const TextStyle(
                color: Colors.black,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLesionMask(BuildContext context) {
    return Positioned(
      top: 150,
      left: 120,
      width: 80,
      height: 60,
      child: Container(
        decoration: BoxDecoration(
          color: Colors.red.withValues(alpha: 0.4),
          borderRadius: BorderRadius.circular(30),
        ),
        child: const Center(
          child: Text(
            'LESION',
            style: TextStyle(
              color: Colors.white,
              fontSize: 10,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTargetHighlight(BuildContext context) {
    return Positioned(
      top: 140,
      left: 110,
      width: 100,
      height: 80,
      child: Container(
        decoration: BoxDecoration(
          border: Border.all(color: AppTheme.emergency, width: 3),
        ),
        child: Align(
          alignment: Alignment.topRight,
          child: Container(
            color: AppTheme.emergency,
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 2),
            child: const Text(
              'TARGET',
              style: TextStyle(
                color: Colors.white,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
