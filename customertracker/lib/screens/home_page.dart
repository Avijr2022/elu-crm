// ignore_for_file: avoid_unnecessary_containers, unused_local_variable, unnecessary_const

import 'package:customertracker/side_menu_app.dart';
import 'package:flutter/material.dart';
import 'package:customertracker/screens/calendar_page.dart';
import 'package:customertracker/theme/colors/light_colors.dart';
import 'package:flutter/services.dart';
import 'package:percent_indicator/percent_indicator.dart';
import 'package:customertracker/widgets/task_column.dart';
import 'package:customertracker/widgets/active_project_card.dart';
import 'package:customertracker/widgets/top_container.dart';

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  Text subheading(String title) {
    return Text(
      title,
      style: const TextStyle(
          color: Color.fromARGB(255, 255, 255, 255),
          fontSize: 20.0,
          fontWeight: FontWeight.w700,
          letterSpacing: 1.2),
    );
  }

  static CircleAvatar calendarIcon() {
    return const CircleAvatar(
      radius: 20.0,
      backgroundColor: Color.fromARGB(132, 48, 148, 151),
      child: Icon(
        Icons.calendar_today,
        size: 20.0,
        color: Colors.white,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    double width = MediaQuery.of(context).size.width;
    return Scaffold(
      backgroundColor: LightColors.kLightYellow,
      drawer: const NavDrawer(),
      appBar: AppBar(
        title: const Text(
          'Welcome Mr. Kedar Gupta',
          style: TextStyle(fontSize: 17),
        ),
        titleTextStyle: const TextStyle(
            color: Color.fromARGB(255, 250, 250, 252),
            fontWeight: FontWeight.w500,
            fontSize: 25),
        elevation: 0,
        backgroundColor: const Color.fromARGB(255, 91, 92, 92),
        systemOverlayStyle: SystemUiOverlayStyle.dark,
      ),
      body: Container(
        padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
        height: 1000,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/cover2.jpg'),
            fit: BoxFit.cover,
          ),
        ),
        child: Container(
          color: const Color.fromARGB(100, 39, 41, 12),
          height: 3000,
          child: SafeArea(
            child: Column(
              children: <Widget>[
                TopContainer(
                  height: 250,
                  width: width,
                  padding: const EdgeInsets.all(5.0),
                  decoration: BoxDecoration(
                      color: const Color.fromARGB(255, 24, 22, 8),
                      border: Border.all(
                        color: const Color.fromARGB(255, 14, 12, 7),
                        width: 4,
                      )),
                  child: Column(
                      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                      children: <Widget>[
                        Padding(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 0, vertical: 0.0),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            children: <Widget>[
                              CircularPercentIndicator(
                                radius: 80.0,
                                lineWidth: 10.0,
                                animation: true,
                                percent: 0.75,
                                circularStrokeCap: CircularStrokeCap.round,
                                progressColor:
                                    const Color.fromARGB(220, 10, 151, 5),
                                backgroundColor:
                                    const Color.fromARGB(255, 252, 251, 251),
                                center: const CircleAvatar(
                                  backgroundColor: LightColors.kBlue,
                                  radius: 35.0,
                                  backgroundImage: AssetImage(
                                    'assets/images/kedargupta.jpg',
                                  ),
                                ),
                              ),
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.center,
                                children: <Widget>[
                                  Container(
                                    child: const Text(
                                      'Kedar Gupta',
                                      textAlign: TextAlign.start,
                                      style: TextStyle(
                                        fontSize: 14.0,
                                        color:
                                            Color.fromARGB(255, 255, 255, 255),
                                        fontWeight: FontWeight.w800,
                                      ),
                                    ),
                                  ),
                                  Container(
                                    child: const Text(
                                      'Business Development',
                                      textAlign: TextAlign.start,
                                      style: TextStyle(
                                        fontSize: 10.0,
                                        color: Colors.black45,
                                        fontWeight: FontWeight.w400,
                                      ),
                                    ),
                                  ),
                                ],
                              )
                            ],
                          ),
                        )
                      ]),
                ),
                Expanded(
                  child: ListView(
                    padding: const EdgeInsets.only(
                        left: 20.0, top: 20.0, right: 20.0),
                    children: [
                      Column(
                        children: <Widget>[
                          Container(
                            color: Colors.transparent,
                            padding: const EdgeInsets.symmetric(
                                horizontal: 10.0, vertical: 10.0),
                            child: Column(
                              children: <Widget>[
                                Row(
                                  crossAxisAlignment: CrossAxisAlignment.center,
                                  mainAxisAlignment:
                                      MainAxisAlignment.spaceBetween,
                                  children: <Widget>[
                                    subheading('My Tasks'),
                                    GestureDetector(
                                      onTap: () {
                                        Navigator.push(
                                          context,
                                          MaterialPageRoute(
                                              builder: (context) =>
                                                  const CalendarPage()),
                                        );
                                      },
                                      child: calendarIcon(),
                                    ),
                                  ],
                                ),
                                const SizedBox(height: 15.0),
                                const TaskColumn(
                                  icon: Icons.alarm,
                                  iconBackgroundColor:
                                      Color.fromARGB(193, 228, 100, 115),
                                  title: 'To Do',
                                  subtitle: '5 tasks now. 1 started',
                                ),
                                const SizedBox(
                                  height: 15.0,
                                ),
                                const TaskColumn(
                                  icon: Icons.blur_circular,
                                  iconBackgroundColor:
                                      Color.fromARGB(179, 249, 191, 124),
                                  title: 'In Progress',
                                  subtitle: '1 tasks now. 1 started',
                                ),
                                const SizedBox(height: 15.0),
                                const TaskColumn(
                                  icon: Icons.check_circle_outline,
                                  iconBackgroundColor:
                                      Color.fromARGB(207, 100, 136, 228),
                                  title: 'Done',
                                  subtitle: '18 tasks now. 13 started',
                                ),
                              ],
                            ),
                          ),
                          Container(
                            color: Colors.transparent,
                            padding: const EdgeInsets.symmetric(
                                horizontal: 5.0, vertical: 5.0),
                            height: 500.0,
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: <Widget>[
                                subheading('Active Projects'),
                                const SizedBox(height: 1.0),
                                const Row(
                                  children: <Widget>[
                                    ActiveProjectsCard(
                                      padding: EdgeInsets.only(
                                          left: 20.0, top: 20.0, right: 20.0),
                                      hight: 15,
                                      cardColor:
                                          Color.fromARGB(164, 48, 148, 151),
                                      loadingPercent: 0.25,
                                      title: 'Education App',
                                      subtitle: '9 hours progress',
                                    ),
                                    SizedBox(width: 20.0),
                                    ActiveProjectsCard(
                                      padding: EdgeInsets.only(
                                          left: 20.0, top: 20.0, right: 20.0),
                                      hight: 15,
                                      cardColor:
                                          Color.fromARGB(164, 228, 100, 115),
                                      loadingPercent: 0.6,
                                      title: 'Making History Notes',
                                      subtitle: '20 hours progress',
                                    ),
                                  ],
                                ),
                                const Row(
                                  children: <Widget>[
                                    ActiveProjectsCard(
                                      padding: EdgeInsets.only(
                                          left: 20.0, top: 20.0, right: 20.0),
                                      hight: 15,
                                      cardColor:
                                          Color.fromARGB(176, 249, 191, 124),
                                      loadingPercent: 0.45,
                                      title: 'WBLDC Project',
                                      subtitle: '5 hours progress',
                                    ),
                                    SizedBox(width: 20.0),
                                    ActiveProjectsCard(
                                      padding: EdgeInsets.only(
                                          left: 20.0, top: 20.0, right: 20.0),
                                      hight: 15,
                                      cardColor:
                                          Color.fromARGB(199, 100, 136, 228),
                                      loadingPercent: 0.9,
                                      title: 'Kolakham Project',
                                      subtitle: '23 hours progress',
                                    ),
                                  ],
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
