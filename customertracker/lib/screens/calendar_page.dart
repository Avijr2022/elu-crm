// ignore_for_file: sized_box_for_whitespace, unused_import

import 'package:customertracker/home_table_event_calendar.dart';
import 'package:customertracker/lead_add_followup.dart';
import 'package:customertracker/lead_event_calendar.dart';
import 'package:customertracker/lead_state.dart';
import 'package:customertracker/set_follow_ups.dart';
import 'package:customertracker/lead_table_event_calendar.dart';
import 'package:flutter/material.dart';
import 'package:customertracker/dates_list.dart';
import 'package:customertracker/theme/colors/light_colors.dart';
import 'package:customertracker/widgets/calendar_dates.dart';
import 'package:customertracker/widgets/task_container.dart';
import 'package:customertracker/screens/create_new_task_page.dart';
import 'package:customertracker/widgets/back_button.dart';

class CalendarPage extends StatelessWidget {
  const CalendarPage({super.key});

  Widget _dashedText() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 15),
      child: const Text(
        '------------------------------------------',
        maxLines: 1,
        style:
            TextStyle(fontSize: 20.0, color: Colors.black12, letterSpacing: 5),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: LightColors.kLightYellow,
      body: Container(
        padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
        height: 1000,
        decoration: const BoxDecoration(
          image: DecorationImage(
            image: AssetImage('assets/images/cover.jpg'),
            fit: BoxFit.cover,
          ),
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(
              20,
              20,
              20,
              0,
            ),
            child: Column(
              children: <Widget>[
                const MyBackButton(),
                const SizedBox(height: 30.0),
                Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: <Widget>[
                      const Text(
                        'Today',
                        style: TextStyle(
                            fontSize: 30.0, fontWeight: FontWeight.w700),
                      ),
                      Container(
                        height: 40.0,
                        width: 120,
                        // decoration: BoxDecoration(
                        //   color: const Color.fromARGB(14, 48, 148, 151),
                        //   borderRadius: BorderRadius.circular(30),
                        // ),
                        child: ElevatedButton(
                          style: ButtonStyle(
                            backgroundColor: WidgetStateProperty.all(
                                const Color.fromARGB(104, 255, 224, 130)),
                            // padding: MaterialStateProperty.all(
                            //     const EdgeInsets.all(50)),
                          ),
                          onPressed: () {
                            Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (context) => const Leadstate(),
                                // const HomeTableEventsCalendar(),
                                // const CreateNewTaskPage(),
                              ),
                            );
                          },
                          child: const Center(
                            child: Text(
                              'Add Task',
                              style: TextStyle(
                                  color: Color.fromARGB(255, 8, 8, 8),
                                  fontWeight: FontWeight.w700,
                                  fontSize: 16),
                            ),
                          ),
                        ),
                      ),
                    ]),
                const SizedBox(height: 10),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.start,
                  children: <Widget>[
                    Text(
                      'Productive Day, Kedar',
                      style: TextStyle(
                        fontSize: 18.0,
                        color: Colors.grey,
                        fontWeight: FontWeight.w400,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 30),
                const Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    'March, 2023',
                    style: TextStyle(fontWeight: FontWeight.w500, fontSize: 15),
                  ),
                ),
                const SizedBox(height: 15.0),
                Container(
                  height: 55.0,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    itemCount: days.length,
                    itemBuilder: (BuildContext context, int index) {
                      return CalendarDates(
                        day: days[index],
                        date: dates[index],
                        dayColor:
                            index == 0 ? LightColors.kRed : Colors.black54,
                        dateColor: index == 0
                            ? LightColors.kRed
                            : LightColors.kDarkBlue,
                      );
                    },
                  ),
                ),
                Expanded(
                  child: SingleChildScrollView(
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 15.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          Expanded(
                            flex: 1,
                            child: ListView.builder(
                              itemCount: time.length,
                              shrinkWrap: true,
                              physics: const NeverScrollableScrollPhysics(),
                              itemBuilder: (BuildContext context, int index) =>
                                  Padding(
                                padding:
                                    const EdgeInsets.symmetric(vertical: 15.0),
                                child: Align(
                                  alignment: Alignment.centerLeft,
                                  child: Text(
                                    '${time[index]} ${time[index] > 8 ? 'PM' : 'AM'}',
                                    style: const TextStyle(
                                      fontSize: 16.0,
                                      color: Colors.black54,
                                    ),
                                  ),
                                ),
                              ),
                            ),
                          ),
                          const SizedBox(
                            width: 20,
                          ),
                          Expanded(
                            flex: 5,
                            child: ListView(
                              shrinkWrap: true,
                              physics: const NeverScrollableScrollPhysics(),
                              children: <Widget>[
                                _dashedText(),
                                const TaskContainer(
                                  title: 'Project Research',
                                  subtitle:
                                      'Discuss with the colleagues about the future plan',
                                  boxColor: LightColors.kLightYellow2,
                                ),
                                _dashedText(),
                                const TaskContainer(
                                  title: 'Work on Medical App',
                                  subtitle: 'Add medicine tab',
                                  boxColor: LightColors.kLavender,
                                ),
                                const TaskContainer(
                                  title: 'Call',
                                  subtitle: 'Call to Shamba Bhanja',
                                  boxColor: LightColors.kPalePink,
                                ),
                                const TaskContainer(
                                  title: 'Design Meeting',
                                  subtitle:
                                      'Discuss with designers for new task for the medical app',
                                  boxColor: LightColors.kLightGreen,
                                ),
                              ],
                            ),
                          )
                        ],
                      ),
                    ),
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
