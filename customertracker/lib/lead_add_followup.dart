// ignore_for_file: sort_child_properties_last, unused_field, no_leading_underscores_for_local_identifiers, unused_local_variable, unused_element, non_constant_identifier_names, use_key_in_widget_constructors, no_logic_in_create_state, unnecessary_const, avoid_print, prefer_typing_uninitialized_variables, unused_import

// import 'package:customertracker/buttontoggleswitch.dart';
import 'package:customertracker/side_menu_app.dart';
import 'package:customertracker/widgets/my_text_field.dart';
import 'package:flutter/material.dart';
// import 'package:flutter_switch/flutter_switch.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';

class FollowupLayout extends StatefulWidget {
  const FollowupLayout({super.key});
  @override
  State<FollowupLayout> createState() => FollowupLayoutState();
}

class FollowupLayoutState extends State<FollowupLayout> {
  bool isToggled = false;

  FollowupLayoutState() {
    _selectvalue = _dropdownlist[0];
    bool isSwitchOn = false;
  }

  final List<String> _dropdownlist = [
    "Tarak Basak",
    "Subhajit Bhattacharya",
    "Avik Dey",
  ];
  String? _selectvalue = "";

  @override
  Widget build(BuildContext context) {
    var GFToggleType;
    return Scaffold(
      // appBar: AppBar(
      //   title: const Text('Set Follow-up'),
      //   backgroundColor: const Color.fromARGB(255, 91, 92, 92),
      //   leading: IconButton(
      //       onPressed: () {
      //         Navigator.pop(context);
      //       },
      //       icon: const Icon(
      //         Icons.arrow_back_ios,
      //         size: 15,
      //         color: Color.fromARGB(255, 248, 247, 247),
      //       )),
      //   // actions: <Widget>[
      //   //   Padding(
      //   //       padding: const EdgeInsets.only(right: 20.0),
      //   //       child: GestureDetector(
      //   //         onTap: () {
      //   //           // Navigator.push(
      //   //           //     context,
      //   //           //     MaterialPageRoute(
      //   //           //         builder: (context) => const SearchPage2()));
      //   //         },
      //   //         child: const Icon(
      //   //           Icons.search,
      //   //           size: 15.0,
      //   //         ),
      //   //       )),
      //   // ],
      // ),

      body: Container(
          padding: const EdgeInsets.only(left: 10.0, right: 10.0),
          decoration: const BoxDecoration(
            image: DecorationImage(
              image: AssetImage('assets/images/cover2.jpg'),
              fit: BoxFit.cover,
            ),
          ),
          child: Column(children: [
            const Row(children: <Widget>[
              Padding(padding: EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 25.0)),
              Text(
                'Assigned To',
                maxLines: 1,
                textAlign: TextAlign.left,
              ),
            ]),
            // const Text('Assigned To', textAlign: TextAlign.left),
            DecoratedBox(
                decoration: BoxDecoration(
                    border: Border.all(width: 1), //border of dropdown button
                    borderRadius: BorderRadius.circular(
                        50), //border raiuds of dropdown button
                    boxShadow: const <BoxShadow>[
                      BoxShadow(
                          color: Color.fromARGB(
                              71, 10, 10, 10), //shadow for button
                          blurRadius: 5) //blur radius of shadow
                    ]),
                child: Padding(
                    padding: const EdgeInsets.only(left: 6, right: 20),
                    child: DropdownButton(
                      value: _selectvalue,
                      items: _dropdownlist
                          .map((e) => DropdownMenuItem(
                                value: e,
                                child: Row(
                                    // mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                    children: [
                                      const Padding(
                                        padding:
                                            EdgeInsets.only(left: 0, right: 0),
                                      ),
                                      const CircleAvatar(
                                        backgroundImage: AssetImage(
                                            'assets/images/cover.jpg'),
                                      ),
                                      // Icon(valueItem.bank_logo),
                                      const SizedBox(
                                        width: 15,
                                      ),
                                      Text(e),
                                    ]),
                              ))
                          .toList(),
                      onChanged: (value) {
                        setState(() {
                          _selectvalue = value as String;
                        });
                      },
                      icon: const Padding(
                          //Icon at tail, arrow bottom is default icon
                          padding: EdgeInsets.only(left: 30),
                          child: Icon(Icons.arrow_drop_down)),
                      iconEnabledColor: Colors.white, //Icon color
                      style: const TextStyle(
                          color:
                              Color.fromARGB(255, 253, 253, 253), //Font color
                          fontSize: 14 //font size on dropdown button
                          ),

                      dropdownColor: const Color.fromARGB(
                          129, 43, 43, 26), //dropdown background color
                      underline: Container(), //remove underline
                      isExpanded: true, //make true to make width 100%
                    ))),
            const Divider(),
            Container(
              padding: const EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 0.0),
              child: const Row(
                children: <Widget>[
                  Icon(FontAwesomeIcons.clock),
                  SizedBox(width: 7, height: 10),
                  Text(
                    'Next follow-up date',
                    maxLines: 1,
                    textAlign: TextAlign.left,
                  ),
                ],
              ),
            ),
            const Padding(
              padding: EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 0.0),
              child: Row(children: <Widget>[
                Padding(padding: EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 25.0)),
                SizedBox(width: 30),
                Text(
                  'Pick date',
                  maxLines: 1,
                  textAlign: TextAlign.left,
                  style: TextStyle(
                    inherit: true,
                  ),
                ),
                SizedBox(width: 180),
                CircleAvatar(
                  backgroundColor: Color.fromARGB(131, 240, 196, 77),
                  radius: 22,
                  child: CircleAvatar(
                    backgroundColor: Color.fromARGB(131, 240, 196, 77),
                    radius: 15,
                    backgroundImage:
                        AssetImage('assets/images/google-calendar.png'),
                  ),
                  // maxRadius: 17,
                  // minRadius: 15,
                ),
              ]),
            ),
            const SizedBox(height: 10),
            // const Divider(),
            Container(
              alignment: Alignment.topLeft,
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Wrap(
                    crossAxisAlignment: WrapCrossAlignment.start,
                    alignment: WrapAlignment.start,
                    verticalDirection: VerticalDirection.down,
                    runSpacing: 5,
                    spacing: 5.0,
                    children: <Widget>[
                      Chip(
                        label:
                            //TextButton(onPressed: onPressed, child: child),
                            Text("       In next 1 hour      "),
                        backgroundColor: Color.fromARGB(75, 0, 0, 0),
                        labelStyle: TextStyle(color: Colors.white),
                      ),
                      Chip(
                        padding: EdgeInsets.only(
                            left: 0.0, top: 0.0, right: 0.0, bottom: 0.0),
                        label: Text(" Tomorrow same time "),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(
              height: 5,
            ),
            Container(
              alignment: Alignment.topLeft,
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  Wrap(
                    crossAxisAlignment: WrapCrossAlignment.start,
                    alignment: WrapAlignment.start,
                    verticalDirection: VerticalDirection.down,
                    runSpacing: 5,
                    spacing: 5.0,
                    children: <Widget>[
                      Chip(
                        label: Text("Next week same time"),
                      ),
                      Chip(
                        label: Text("           Custom           "),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 5),
            const MyTextField(
              label: 'What to do on next follow-up?',
              minLines: 1,
              maxLines: 3,
              icon: Icon(Icons.mic),
            ),
            const SizedBox(height: 5),
            Container(
              padding: const EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 0.0),
              child: const Row(
                children: <Widget>[
                  Icon(Icons.find_replace_outlined),
                  SizedBox(width: 7, height: 10),
                  Text(
                    'Repeat Follow-up',
                    maxLines: 1,
                    textAlign: TextAlign.left,
                  ),
                  SizedBox(width: 150),
                  Icon(Icons.toggle_off_outlined)
                ],
              ),
            ),

            const Divider(),
            Container(
              padding: const EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 0.0),
              child: const Row(
                children: <Widget>[
                  Icon(Icons.notifications),
                  SizedBox(width: 7, height: 10),
                  Text(
                    'On-time follow-up reminder',
                    maxLines: 1,
                    textAlign: TextAlign.left,
                  ),
                  SizedBox(width: 85),
                  Icon(Icons.toggle_off_outlined)
                ],
              ),
            ),
            const Divider(),
            Container(
              padding: const EdgeInsets.fromLTRB(0.0, 0.0, 0.0, 0.0),
              child: const Row(
                children: <Widget>[
                  Icon(Icons.notifications_off),
                  SizedBox(width: 7, height: 10),
                  Text(
                    'Do not follow-up',
                    maxLines: 1,
                    textAlign: TextAlign.left,
                  ),
                  SizedBox(width: 155),
                  Icon(Icons.toggle_off_outlined)
                ],
              ),
            ),
          ])),
    );
  }

// @override
// State<StatefulWidget> createState() {
//   throw UnimplementedError();
}
