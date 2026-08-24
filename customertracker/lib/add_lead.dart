// ignore_for_file: unnecessary_const, avoid_unnecessary_containers, unused_import, unnecessary_null_comparison, avoid_print

import 'package:customertracker/lead_add_followup.dart';
import 'package:customertracker/lead_add_qualifiers.dart';
import 'package:customertracker/lead_select_list.dart';
import 'package:flutter/material.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:dropdown_button2/dropdown_button2.dart';

class Addleadbarstate extends StatelessWidget {
  const Addleadbarstate({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: DefaultTabController(
        length: 3,
        child: Scaffold(
          appBar: AppBar(
            backgroundColor: const Color.fromARGB(255, 91, 92, 92),
            leading: IconButton(
                onPressed: () {
                  Navigator.pop(context);
                },
                icon: const Icon(
                  Icons.arrow_back_ios,
                  size: 15,
                  color: Color.fromARGB(255, 248, 247, 247),
                )),
            bottom: const TabBar(
              tabs: [
                Tab(text: "PROFILE"),
                Tab(text: "QUALIFIERS"),
                Tab(text: "FOLLOW-UP"),
              ],
            ),
            actions: <Widget>[
              Padding(
                  padding: const EdgeInsets.only(
                      right: 20.0, left: 20.0, top: 20.0, bottom: 20.0),
                  child: GestureDetector(
                    onTap: () {},
                    child: const Text('Save'),
                  )),
            ],
            title: const Text('Add Lead'),
          ),
          body: Container(
            padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
            height: 1000,
            decoration: const BoxDecoration(
              image: DecorationImage(
                image: AssetImage('assets/images/cover.jpg'),
                fit: BoxFit.cover,
              ),
            ),
            child: TabBarView(
              children: <Widget>[
                Center(
                  child: SingleChildScrollView(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: <Widget>[
                        Container(
                          child: const CircleAvatar(
                            backgroundColor: Color.fromARGB(88, 255, 255, 255),
                            minRadius: 44.0,
                            child: Center(
                              child: CircleAvatar(
                                backgroundColor:
                                    Color.fromARGB(255, 148, 151, 151),
                                radius: 40.0,
                                backgroundImage: null,
                                child: ClipOval(
                                  child: SizedBox(
                                    width: 180.0,
                                    height: 180.0,
                                    child: Icon(Icons.camera),
                                  ),
                                ),
                              ),
                            ),
                          ),
                        ),
                        const Divider(
                          color: Color.fromARGB(255, 42, 90, 250),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton2<String>(
                              isExpanded: true,
                              hint: Text(
                                'Select List',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Theme.of(context).hintColor,
                                ),
                              ),
                              items: items
                                  .map((item) => DropdownMenuItem(
                                        value: item,
                                        child: Text(
                                          item,
                                          style: const TextStyle(
                                            fontSize: 14,
                                          ),
                                        ),
                                      ))
                                  .toList(),
                              value: selectedValue,
                              onChanged: (value) {
                                setState(() {
                                  selectedValue = value as String;
                                });
                              },
                              buttonStyleData: const ButtonStyleData(
                                height: 40,
                                width: 230,
                              ),
                              dropdownStyleData: const DropdownStyleData(
                                maxHeight: 200,
                              ),
                              menuItemStyleData: const MenuItemStyleData(
                                height: 40,
                              ),
                              dropdownSearchData: DropdownSearchData(
                                searchController: textEditingController,
                                searchInnerWidgetHeight: 40,
                                searchInnerWidget: Container(
                                  height: 40,
                                  padding: const EdgeInsets.only(
                                    top: 8,
                                    bottom: 4,
                                    right: 8,
                                    left: 8,
                                  ),
                                  child: TextFormField(
                                    expands: true,
                                    maxLines: null,
                                    controller: textEditingController,
                                    decoration: InputDecoration(
                                      icon: const Icon(Icons.gpp_good),
                                      isDense: true,
                                      contentPadding:
                                          const EdgeInsets.symmetric(
                                        horizontal: 10,
                                        vertical: 8,
                                      ),
                                      hintText: 'Search List',
                                      hintStyle: const TextStyle(fontSize: 16),
                                      border: OutlineInputBorder(
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                    ),
                                  ),
                                ),
                                searchMatchFn: (item, searchValue) {
                                  return (item.value
                                      .toString()
                                      .contains(searchValue));
                                },
                              ),
                              //This to clear the search value when you close the menu
                              onMenuStateChange: (isOpen) {
                                if (!isOpen) {
                                  textEditingController.clear();
                                }
                              },
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(83, 245, 246, 247),
                          ),
                          child: TextFormField(
                            decoration: const InputDecoration(
                              icon: Icon(Icons.person),
                              hintText: 'Enter your First Name',
                              labelText: 'First Name',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(83, 245, 246, 247),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.person),
                              hintText: 'Enter your Last Name',
                              labelText: 'Last Name',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(83, 245, 246, 247),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.boy),
                              hintText: 'Enter your Designation',
                              labelText: 'Designation',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(82, 245, 245, 247),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.calculate_outlined),
                              hintText: 'Enter your Organisation Name',
                              labelText: 'Organisation Name',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(83, 245, 246, 247),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.collections),
                              hintText: 'Organisation website',
                              labelText: 'Organisation website',
                            ),
                          ),
                          // const Divider(
                          //   color: Color.fromARGB(255, 42, 90, 250),
                          // ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(85, 226, 232, 238),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.email),
                              hintText: 'Enter a email address',
                              labelText: 'Email',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(85, 226, 232, 238),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.phone),
                              hintText: 'Enter a phone number',
                              labelText: 'Phone',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(85, 226, 232, 238),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.route),
                              hintText: 'Address line 1',
                              labelText: 'Address line 1',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(85, 226, 232, 238),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.alt_route),
                              hintText: 'Address line 2',
                              labelText: 'Address line 2',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(85, 226, 232, 238),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(FontAwesomeIcons.city),
                              hintText: 'Enter your City',
                              labelText: 'City',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(85, 226, 232, 238),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.gps_fixed),
                              hintText: 'Enter your State',
                              labelText: 'State',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(85, 226, 232, 238),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.pin_drop),
                              hintText: 'Enter your ZIP Code',
                              labelText: 'ZIP',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(85, 226, 232, 238),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(FontAwesomeIcons.globe),
                              hintText: 'Enter your Country',
                              labelText: 'Country',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(82, 204, 205, 211),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(FontAwesomeIcons.gitlab),
                              hintText: 'Gitlab URL',
                              labelText: 'Gitlab URL',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(82, 204, 205, 211),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(
                                FontAwesomeIcons.twitter,
                              ),
                              hintText: 'Twitter URL',
                              labelText: 'Twitter URL',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(82, 204, 205, 211),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.facebook),
                              hintText: 'Facebook URL',
                              labelText: 'Facebook URL',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(82, 204, 205, 211),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(FontAwesomeIcons.instagram),
                              hintText: 'Instagram URL',
                              labelText: 'Instagram URL',
                            ),
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.only(left: 10.0, top: 0.0),
                          height: 50,
                          decoration: const BoxDecoration(
                            color: Color.fromARGB(82, 204, 205, 211),
                          ),
                          child: const TextField(
                            decoration: InputDecoration(
                              icon: Icon(Icons.account_box),
                              hintText: 'Account Owner',
                              labelText: 'Account Owner',
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
                const QualifiersLayout(),
                const FollowupLayout(),
                // Icon(Icons.details),
                // Icon(Icons.perm_identity),
                // const Icon(Icons.follow_the_signs),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

void setState(Null Function() selectedValue) {
  if (selectedValue != null) {
    selectedValue();
  } else {
    print('No function selected.');
  }
}

final List<String> items = [
  '--Select List--',
  'Call Logs',
  'Existing Leads',
  'Phone Contacts',
  'Sample Leads',
  'Website Enquires',
];

String? selectedValue;
final TextEditingController textEditingController = TextEditingController();
