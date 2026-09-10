// ignore_for_file: prefer_typing_uninitialized_variables

import 'package:flutter/material.dart';
import 'package:syncfusion_flutter_charts/charts.dart';

@override
Widget build(BuildContext context) {
  final List<ChartData> chartData = [
    ChartData('Kedar Gupta', 25),
    ChartData('Shamba Bhanja', 38),
    ChartData('Ranadeep Dhar', 34),
    ChartData('Amalendu Chatterjee', 52)
  ];

  return Scaffold(
      body: Center(
          child: SfPyramidChart(
              series: PyramidSeries<ChartData, String>(
                  dataSource: chartData,
                  xValueMapper: (ChartData data, _) => data.x,
                  yValueMapper: (ChartData data, _) => data.y))));
}

class ChartData {
  ChartData(this.x, this.y);
  final String x;
  final double y;
  final Color color = const Color.fromARGB(255, 256, 257, 255);
}
