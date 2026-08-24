// ignore_for_file: sized_box_for_whitespace, avoid_print, prefer_const_constructors, avoid_unnecessary_containers, unnecessary_import

import 'package:customertracker/add_lead.dart';
import 'package:flutter/animation.dart';
import 'package:flutter/material.dart';

class Leadrecentactivity extends StatefulWidget {
  const Leadrecentactivity({super.key});

  @override
  LeadrecentactivityState createState() => LeadrecentactivityState();
}

class LeadrecentactivityState extends State<Leadrecentactivity>
    with TickerProviderStateMixin {
  int _angle = 90;
  bool _isRotated = true;

  late AnimationController _controller;
  late Animation<double> _animation;
  late Animation<double> _animation2;

  @override
  void initState() {
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 180),
    );

    _animation = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.0, 1.0, curve: Curves.linear),
    );

    _animation2 = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.5, 1.0, curve: Curves.linear),
    );

    _controller.reverse();
    super.initState();
  }

  void _rotate() {
    setState(() {
      if (_isRotated) {
        _angle = 45;
        _isRotated = false;
        _controller.forward();
      } else {
        _angle = 90;
        _isRotated = true;
        _controller.reverse();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: const Text(
            "xxxxx",
            style: TextStyle(color: Color.fromARGB(255, 250, 249, 249)),
          ),
          leading: Padding(
              padding: const EdgeInsets.only(right: 20.0),
              child: GestureDetector(
                onTap: () {
                  Navigator.pop(context);
                },
                child: const Icon(Icons.arrow_back_ios_new),
              )),
          // title: const Text(title),

          backgroundColor: const Color.fromARGB(100, 22, 44, 33),
        ),
        body: Stack(children: <Widget>[
          Positioned(
              bottom: 280.0,
              right: 24.0,
              child: Row(
                children: <Widget>[
                  ScaleTransition(
                    scale: _animation2,
                    alignment: FractionalOffset.center,
                    child: Container(
                      margin: const EdgeInsets.only(right: 16.0),
                      child: SizedBox(
                        width: 150.0,
                        height: 30.0,
                        child: Card(
                          color: Color.fromARGB(115, 7, 7, 7),
                          child: Center(
                            child: Text(
                              'All Activities',
                              style: TextStyle(color: Colors.white),
                            ), //Text
                          ), //Center
                        ), //Card
                      ),
                    ),
                  ),
                  ScaleTransition(
                    scale: _animation2,
                    alignment: FractionalOffset.center,
                    child: Material(
                        color: Color.fromARGB(255, 35, 109, 12),
                        type: MaterialType.circle,
                        elevation: 6.0,
                        child: GestureDetector(
                          child: Container(
                              width: 40.0,
                              height: 40.0,
                              child: InkWell(
                                onTap: () {
                                  if (_angle == 45.0) {
                                    print("All Activities");
                                  }
                                },
                                child: const Center(
                                  child: Icon(
                                    Icons.filter_alt,
                                    color: Color(0xFFFFFFFF),
                                  ),
                                ),
                              )),
                        )),
                  ),
                ],
              )),
          Positioned(
              bottom: 230.0,
              right: 24.0,
              child: Row(
                children: <Widget>[
                  ScaleTransition(
                    scale: _animation2,
                    alignment: FractionalOffset.center,
                    child: Container(
                      margin: const EdgeInsets.only(right: 16.0),
                      child: SizedBox(
                        width: 150.0,
                        height: 30.0,
                        child: Card(
                          color: Color.fromARGB(115, 7, 7, 7),
                          child: Center(
                            child: Text(
                              'Comments',
                              style: TextStyle(color: Colors.white),
                            ), //Text
                          ), //Center
                        ), //Card
                      ),
                    ),
                  ),
                  ScaleTransition(
                    scale: _animation2,
                    alignment: FractionalOffset.center,
                    child: Material(
                        color: const Color(0xFF00BFA5),
                        type: MaterialType.circle,
                        elevation: 6.0,
                        child: GestureDetector(
                          child: Container(
                              width: 40.0,
                              height: 40.0,
                              child: InkWell(
                                onTap: () {
                                  if (_angle == 45.0) {
                                    print("Comments");
                                  }
                                },
                                child: const Center(
                                  child: Icon(
                                    Icons.chat_sharp,
                                    color: Color(0xFFFFFFFF),
                                  ),
                                ),
                              )),
                        )),
                  ),
                ],
              )),
          Positioned(
              bottom: 180.0,
              right: 24.0,
              child: Container(
                child: Row(
                  children: <Widget>[
                    ScaleTransition(
                      scale: _animation,
                      alignment: FractionalOffset.center,
                      child: Container(
                        margin: const EdgeInsets.only(right: 16.0),
                        child: SizedBox(
                          width: 150.0,
                          height: 30.0,
                          child: Card(
                            color: Color.fromARGB(115, 7, 7, 7),
                            child: Center(
                              child: Text(
                                'System Logs',
                                style: TextStyle(color: Colors.white),
                              ), //Text
                            ), //Center
                          ), //Card
                        ),
                      ),
                    ),
                    ScaleTransition(
                      scale: _animation,
                      alignment: FractionalOffset.center,
                      child: Material(
                          color: Color.fromARGB(255, 182, 68, 192),
                          type: MaterialType.circle,
                          elevation: 6.0,
                          child: GestureDetector(
                            child: Container(
                                width: 40.0,
                                height: 40.0,
                                child: InkWell(
                                  onTap: () {
                                    if (_angle == 45.0) {
                                      print("System Logs");
                                    }
                                  },
                                  child: const Center(
                                    child: Icon(
                                      Icons.laptop_mac_outlined,
                                      color: Color(0xFFFFFFFF),
                                    ),
                                  ),
                                )),
                          )),
                    ),
                  ],
                ),
              )),
          Positioned(
              bottom: 130.0,
              right: 24.0,
              child: Container(
                child: Row(
                  children: <Widget>[
                    ScaleTransition(
                      scale: _animation,
                      alignment: FractionalOffset.center,
                      child: Container(
                        margin: const EdgeInsets.only(right: 16.0),
                        child: SizedBox(
                          width: 150.0,
                          height: 30.0,
                          child: Card(
                            color: Color.fromARGB(115, 7, 7, 7),
                            child: Center(
                              child: Text(
                                'Attachments',
                                style: TextStyle(color: Colors.white),
                              ), //Text
                            ), //Center
                          ), //Card
                        ),
                      ),
                    ),
                    ScaleTransition(
                      scale: _animation,
                      alignment: FractionalOffset.center,
                      child: Material(
                          color: Color.fromARGB(255, 224, 138, 56),
                          type: MaterialType.circle,
                          elevation: 6.0,
                          child: GestureDetector(
                            child: Container(
                                width: 40.0,
                                height: 40.0,
                                child: InkWell(
                                  onTap: () {
                                    if (_angle == 45.0) {
                                      print("Attachments");
                                    }
                                  },
                                  child: const Center(
                                    child: Icon(
                                      Icons.attachment_sharp,
                                      color: Color(0xFFFFFFFF),
                                    ),
                                  ),
                                )),
                          )),
                    ),
                  ],
                ),
              )),
          Positioned(
              bottom: 80.0,
              right: 24.0,
              child: Container(
                child: Row(
                  children: <Widget>[
                    ScaleTransition(
                      scale: _animation,
                      alignment: FractionalOffset.center,
                      child: Container(
                        margin: const EdgeInsets.only(right: 16.0),
                        child: SizedBox(
                          width: 150.0,
                          height: 30.0,
                          child: Card(
                            color: Color.fromARGB(115, 7, 7, 7),
                            child: Center(
                              child: Text(
                                'By Team',
                                style: TextStyle(color: Colors.white),
                              ), //Text
                            ), //Center
                          ), //Card
                        ),
                      ),
                    ),
                    ScaleTransition(
                      scale: _animation,
                      alignment: FractionalOffset.center,
                      child: Material(
                          color: Color.fromARGB(255, 230, 184, 36),
                          type: MaterialType.circle,
                          elevation: 6.0,
                          child: GestureDetector(
                            child: Container(
                                width: 40.0,
                                height: 40.0,
                                child: InkWell(
                                  onTap: () {
                                    if (_angle == 45.0) {
                                      print("By Team");
                                    }
                                  },
                                  child: const Center(
                                    child: Icon(
                                      Icons.groups_outlined,
                                      color: Color(0xFFFFFFFF),
                                    ),
                                  ),
                                )),
                          )),
                    ),
                  ],
                ),
              )),
          Positioned(
            bottom: 16.0,
            right: 16.0,
            child: Material(
                color: Color.fromARGB(255, 40, 122, 23),
                type: MaterialType.circle,
                elevation: 5.0,
                child: GestureDetector(
                  child: Container(
                      width: 50.0,
                      height: 50.00,
                      child: InkWell(
                        onTap: _rotate,
                        child: Center(
                            child: RotationTransition(
                          turns: AlwaysStoppedAnimation(_angle / 360),
                          child: const Icon(
                            Icons.filter_alt,
                            color: Color(0xFFFFFFFF),
                          ),
                        )),
                      )),
                )),
          ),
        ]));
  }
}
