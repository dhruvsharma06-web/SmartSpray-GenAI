import 'package:flutter/material.dart';
import '../features/detection/detection_provider.dart';

class DetectionVisualizer extends StatelessWidget {
  final DetectionState state;

  const DetectionVisualizer({super.key, required this.state});

  @override
  Widget build(BuildContext context) {
    if (state.status == DetectionStatus.idle) {
      return Container(
        height: 200,
        alignment: Alignment.center,
        color: Colors.grey[200],
        child: const Text('Ready for scan'),
      );
    }

    // Simulate generic view. Actual image is on Laptop.
    return Container(
        height: 200,
        alignment: Alignment.center,
        color: Colors.black12,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.laptop_chromebook, size: 48, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              'Laptop processing frame...',
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      );
  }
}
