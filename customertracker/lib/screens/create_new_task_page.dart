// ignore_for_file: avoid_unnecessary_containers, sized_box_for_whitespace, sort_child_properties_last, prefer_const_constructors, unnecessary_const

import 'package:flutter/material.dart';
import 'package:customertracker/theme/colors/light_colors.dart';
import 'package:customertracker/widgets/top_container.dart';
import 'package:customertracker/widgets/back_button.dart';
import 'package:customertracker/widgets/my_text_field.dart';
import 'package:customertracker/screens/home_page.dart';
import 'package:flutter/services.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class CreateNewTaskPage extends StatelessWidget {
  const CreateNewTaskPage({super.key});

  @override
  Widget build(BuildContext context) {
    double width = MediaQuery.of(context).size.width;
    var downwardIcon = const Icon(
      Icons.keyboard_arrow_down,
      color: Colors.black54,
    );
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Add Event',
          style: TextStyle(fontSize: 17),
        ),
        titleTextStyle: const TextStyle(
            color: Color.fromARGB(255, 250, 252, 252),
            fontWeight: FontWeight.w500,
            fontSize: 25),
        elevation: 0,
        backgroundColor: const Color.fromARGB(255, 91, 92, 92),
        systemOverlayStyle: SystemUiOverlayStyle.dark,
      ),
      body: Container(
        padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
        height: 700,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/cover.jpg'),
            fit: BoxFit.cover,
          ),
        ),
        child: SafeArea(
          child: Column(
            children: <Widget>[
              TopContainer(
                padding: const EdgeInsets.fromLTRB(20, 20, 20, 40),
                width: width,
                height: 0.0,
                decoration: BoxDecoration(
                    color: Colors.yellow[100],
                    border: Border.all(
                      color: Colors.red,
                      width: 5,
                    )),
                child: Column(
                  children: <Widget>[
                    const MyBackButton(),
                    const SizedBox(
                      height: 30,
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.start,
                      children: const <Widget>[
                        Text(
                          'Create new task',
                          style: TextStyle(
                              fontSize: 25.0, fontWeight: FontWeight.w700),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    Container(
                        child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        MyTextField(
                          label: 'Title',
                          icon: Icon(FontAwesomeIcons.font),
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.start,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: <Widget>[
                            Expanded(
                              child: MyTextField(
                                label: 'Date',
                                icon: downwardIcon,
                              ),
                            ),
                            HomePage.calendarIcon(),
                          ],
                        )
                      ],
                    ))
                  ],
                ),
              ),
              Expanded(
                  child: SingleChildScrollView(
                padding: const EdgeInsets.symmetric(horizontal: 20),
                child: Column(
                  children: <Widget>[
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: <Widget>[
                        Expanded(
                            child: MyTextField(
                          label: 'Start Time',
                          icon: downwardIcon,
                        )),
                        const SizedBox(width: 40),
                        Expanded(
                          child: MyTextField(
                            label: 'End Time',
                            icon: downwardIcon,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    const MyTextField(
                      label: 'Description',
                      minLines: 3,
                      maxLines: 3,
                      icon: Icon(Icons.abc),
                    ),
                    const SizedBox(height: 20),
                    Container(
                      alignment: Alignment.topLeft,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const <Widget>[
                          Text(
                            'Category',
                            style: TextStyle(
                              fontSize: 18,
                              color: Colors.black54,
                            ),
                          ),
                          Wrap(
                            crossAxisAlignment: WrapCrossAlignment.start,
                            //direction: Axis.vertical,
                            alignment: WrapAlignment.start,
                            verticalDirection: VerticalDirection.down,
                            runSpacing: 5,
                            //textDirection: TextDirection.rtl,
                            spacing: 10.0,
                            children: <Widget>[
                              Chip(
                                label: Text("SPORT APP"),
                                backgroundColor: LightColors.kRed,
                                labelStyle: TextStyle(color: Colors.white),
                              ),
                              Chip(
                                padding: EdgeInsets.only(
                                    left: 0.0,
                                    top: 0.0,
                                    right: 0.0,
                                    bottom: 0.0),
                                label: Text("MEDICAL APP"),
                              ),
                              Chip(
                                label: Text("RENT APP"),
                              ),
                              Chip(
                                label: Text("NOTES"),
                              ),
                              Chip(
                                label: Text("GAMING PLATFORM APP"),
                              ),
                            ],
                          ),
                        ],
                      ),
                    )
                  ],
                ),
              )),
              Container(
                height: 80,
                width: width,
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    Container(
                      child: const Text(
                        'Create Task',
                        style: TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.w700,
                            fontSize: 18),
                      ),
                      alignment: Alignment.center,
                      margin: const EdgeInsets.fromLTRB(20, 10, 20, 20),
                      width: width - 40,
                      decoration: BoxDecoration(
                        color: LightColors.kBlue,
                        borderRadius: BorderRadius.circular(30),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
