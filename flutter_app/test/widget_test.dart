import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_app/app/app.dart';

void main() {
  testWidgets('App loads smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      const ProviderScope(
        child: SmartSprayApp(),
      ),
    );

    await tester.pumpAndSettle();

    // Verify that our home screen loads
    expect(find.text('SMARTSPRAY'), findsOneWidget);
  });
}
