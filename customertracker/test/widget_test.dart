// Smoke tests for the customertracker app widgets.
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:customertracker/widgets/my_text_field.dart';

void main() {
  testWidgets('MyTextField renders its label and accepts input',
      (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(
      home: Scaffold(
        body: MyTextField(label: 'Customer name', icon: Icon(Icons.person)),
      ),
    ));

    expect(find.text('Customer name'), findsOneWidget);
    expect(find.byType(TextField), findsOneWidget);

    await tester.enterText(find.byType(TextField), 'Acme Ltd');
    await tester.pump();
    expect(find.text('Acme Ltd'), findsOneWidget);
  });
}
