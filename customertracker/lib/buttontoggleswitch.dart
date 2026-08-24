// ignore_for_file: avoid_print

import 'package:flutter/material.dart';

class StyledSwitch extends StatefulWidget {
  final void Function(bool isToggled) onToggled;

  const StyledSwitch({super.key, required this.onToggled});

  @override
  State<StyledSwitch> createState() => _StyledSwitchState();
}

class _StyledSwitchState extends State<StyledSwitch> {
  bool isToggled = false;
  double size = 30;
  double innerPadding = 0;

  @override
  void initState() {
    innerPadding = size / 10;
    super.initState();
  }

  bool isSwitchOn = false;

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        setState(() => isToggled = !isToggled);
        widget.onToggled(isToggled);
      },
      onPanEnd: (b) {
        setState(() => isToggled = !isToggled);
        widget.onToggled(isToggled);
      },
      child: AnimatedContainer(
        height: size,
        width: size * 2,
        padding: EdgeInsets.all(innerPadding),
        alignment: isToggled ? Alignment.centerLeft : Alignment.centerRight,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(50),
          color: isToggled ? Colors.blue.shade100 : Colors.grey.shade300,
        ),
        child: Container(
          width: size - innerPadding * 2,
          height: size - innerPadding * 2,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(100),
            color: isToggled ? Colors.blue.shade600 : Colors.grey.shade500,
          ),
        ),
      ),
    );
  }

  void handleToggle(bool isToggled) {
    setState(() {
      isSwitchOn = isToggled;
    });

    if (isSwitchOn) {
      print('Switch is on');
    } else {
      print('Switch is off');
    }
  }
}
