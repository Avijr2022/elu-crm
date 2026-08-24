// ignore_for_file: unnecessary_null_comparison, duplicate_import, unused_import

import 'package:customertracker/theme/colors/light_colors.dart';
import 'package:flutter/material.dart';

class TopContainer extends StatelessWidget {
  final double height;
  final double width;
  final Widget child;
  final EdgeInsets padding;
  const TopContainer(
      {super.key,
      required this.height,
      required this.width,
      required this.child,
      required this.padding,
      required BoxDecoration decoration});

  @override
  Widget build(BuildContext context) {
    return Container(
      // ignore: prefer_if_null_operators
      padding: padding != null
          ? padding
          : const EdgeInsets.symmetric(horizontal: 20.0),
      decoration: const BoxDecoration(
          color: Color.fromARGB(108, 236, 236, 236),
          borderRadius: BorderRadius.only(
            bottomRight: Radius.circular(40.0),
            bottomLeft: Radius.circular(40.0),
          )),
      height: height,
      width: width,
      child: child,
    );
  }
}
