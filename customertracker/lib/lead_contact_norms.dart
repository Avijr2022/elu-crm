// ignore_for_file: sized_box_for_whitespace, avoid_print, prefer_const_constructors, avoid_unnecessary_containers, unnecessary_import

import 'package:customertracker/add_lead.dart';
import 'package:customertracker/lead_contacts.dart';
import 'package:flutter/animation.dart';
import 'package:flutter/material.dart';

// void main() {
//   runApp(MaterialApp(home: LeadContactNorms()));
// }

class LeadContactNorms extends StatefulWidget {
  const LeadContactNorms({super.key});

  @override
  LeadContactNormsState createState() => LeadContactNormsState();
}

class LeadContactNormsState extends State<LeadContactNorms>
    with TickerProviderStateMixin {
  int _angle = 90;
  bool _isRotated = true;

  late AnimationController _controller;
  late Animation<double> _animation;
  late Animation<double> _animation2;
  late Animation<double> _animation3;

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

    _animation3 = CurvedAnimation(
      parent: _controller,
      curve: const Interval(0.8, 1.0, curve: Curves.linear),
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
        body: Stack(children: <Widget>[
      AllLeadsPage(),
      Positioned(
          bottom: 280.0,
          right: 24.0,
          child: Container(
            child: Row(
              children: <Widget>[
                ScaleTransition(
                  scale: _animation3,
                  alignment: FractionalOffset.center,
                  child: Container(
                    margin: const EdgeInsets.only(right: 16.0),
                    child: SizedBox(
                      width: 120.0,
                      height: 30.0,
                      child: Card(
                        color: Color.fromARGB(115, 7, 7, 7),
                        child: Center(
                          child: Text(
                            'Add Lead Form',
                            style: TextStyle(color: Colors.white),
                          ), //Text
                        ), //Center
                      ), //Card
                    ), //SizedBox
                  ),
                ),
                ScaleTransition(
                  scale: _animation3,
                  alignment: FractionalOffset.center,
                  child: Material(
                      color: Color.fromARGB(234, 219, 98, 98),
                      type: MaterialType.circle,
                      elevation: 6.0,
                      child: GestureDetector(
                        child: Container(
                            width: 40.0,
                            height: 40.0,
                            child: InkWell(
                              onTap: () {
                                Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                        builder: (context) =>
                                            Addleadbarstate()));

                                if (_angle == 45.0) {
                                  print("Add Lead Form");
                                }
                              },
                              child: Center(
                                child: const Icon(
                                  Icons.playlist_add_circle_sharp,
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
                    width: 120.0,
                    height: 30.0,
                    child: Card(
                      color: Color.fromARGB(115, 7, 7, 7),
                      child: Center(
                        child: Text(
                          'Import Contacts',
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
                                print("Import Contacts");
                              }
                            },
                            child: const Center(
                              child: Icon(
                                Icons.import_contacts_outlined,
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
                            'Add From Call Logs',
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
                      color: const Color(0xFFE57373),
                      type: MaterialType.circle,
                      elevation: 6.0,
                      child: GestureDetector(
                        child: Container(
                            width: 40.0,
                            height: 40.0,
                            child: InkWell(
                              onTap: () {
                                if (_angle == 45.0) {
                                  print("Add From Call Logs");
                                }
                              },
                              child: const Center(
                                child: Icon(
                                  Icons.contact_page,
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
                            'Add From WhatsApp Logs',
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
                      color: Color.fromARGB(255, 74, 143, 61),
                      type: MaterialType.circle,
                      elevation: 6.0,
                      child: GestureDetector(
                        child: Container(
                            width: 40.0,
                            height: 40.0,
                            child: InkWell(
                              onTap: () {
                                if (_angle == 45.0) {
                                  print("Add From WhatsApp Logs");
                                }
                              },
                              child: const Center(
                                child: Icon(
                                  Icons.apartment,
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
                      width: 110.0,
                      height: 30.0,
                      child: Card(
                        color: Color.fromARGB(115, 7, 7, 7),
                        child: Center(
                          child: Text(
                            'Integrations',
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
                                  print("Integrations");
                                }
                              },
                              child: const Center(
                                child: Icon(
                                  Icons.settings_suggest_outlined,
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
            color: Color.fromARGB(104, 80, 63, 63),
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
                        Icons.add,
                        color: Color(0xFFFFFFFF),
                      ),
                    )),
                  )),
            )),
      ),
    ]));
  }
}
