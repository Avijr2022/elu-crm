// ignore_for_file: sort_child_properties_last, unused_import, use_super_parameters

import 'package:customertracker/lead_state.dart';
import 'package:customertracker/login_otp.dart';
import 'package:customertracker/home.dart';
import 'package:customertracker/screens/home_page.dart';
import 'package:flutter/material.dart';
import 'forgot_password.dart' show ForgotPassword;
import 'register.dart' show SignupPage;
// import 'package:flutter_signin_button/flutter_signin_button.dart';

void main() => runApp(const MyApp());

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  static const String _title = 'Lead Tracking System';

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: _title,
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        appBar: AppBar(
          backgroundColor: const Color.fromARGB(255, 91, 92, 92),
          title: const Text(_title),
        ),
        body: Container(
          padding: const EdgeInsets.only(left: 20.0, top: 20.0, right: 20.0),
          height: 1000,
          // decoration: const BoxDecoration(
          //   image: DecorationImage(
          //     image: AssetImage('assets/images/cover.jpg'),
          //     fit: BoxFit.cover,
          //   ),
          // ),
          child: const MyStatefulWidget(),
        ),
      ),
    );
  }
}

class MyStatefulWidget extends StatefulWidget {
  const MyStatefulWidget({Key? key}) : super(key: key);

  @override
  State<MyStatefulWidget> createState() => _MyStatefulWidgetState();
}

class _MyStatefulWidgetState extends State<MyStatefulWidget> {
  TextEditingController nameController = TextEditingController();
  TextEditingController passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Padding(
        padding: const EdgeInsets.all(10),
        child: ListView(
          children: <Widget>[
            Container(
                alignment: Alignment.center,
                padding: const EdgeInsets.all(10),
                child: const Text(
                  'TECH IT EASY',
                  style: TextStyle(
                      color: Color.fromARGB(255, 91, 92, 92),
                      fontWeight: FontWeight.w500,
                      fontSize: 25),
                )),
            Container(
                alignment: Alignment.center,
                padding: const EdgeInsets.all(10),
                child: const Text(
                  'Login',
                  style: TextStyle(
                    fontSize: 20,
                    color: Color.fromARGB(255, 91, 92, 92),
                  ),
                )),
            Container(
              padding: const EdgeInsets.all(10),
              child: TextField(
                controller: nameController,
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.email),
                  border: OutlineInputBorder(),
                  labelText: 'Business Email',
                ),
              ),
            ),
            Container(
              padding: const EdgeInsets.fromLTRB(10, 10, 10, 0),
              child: TextField(
                obscureText: true,
                controller: passwordController,
                decoration: const InputDecoration(
                  prefixIcon: Icon(Icons.key),
                  suffixIcon: Icon(Icons.remove_red_eye),
                  border: OutlineInputBorder(),
                  labelText: 'Password',
                ),
              ),
            ),
            Container(
              height: 70,
              padding: const EdgeInsets.fromLTRB(10, 30, 10, 0),
              child: MaterialButton(
                minWidth: double.infinity,
                height: 60,
                // disabledColor: const Color.fromARGB(255, 121, 119, 119),
                onPressed: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const HomePage()));
                },
                color: const Color.fromARGB(100, 22, 44, 33),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(40)),
                child: const Text(
                  "Login",
                  style: TextStyle(
                    color: Color.fromARGB(214, 255, 255, 255),
                    fontWeight: FontWeight.w600,
                    fontSize: 16,
                  ),
                ),
              ),
            ),
            // const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.fromLTRB(10, 30, 10, 0),
              // child: SignInButton(

              //   Buttons.Google,
              //   text: "Sign up with Google",
              //   onPressed: () {
              //     Navigator.push(
              //         context,
              //         MaterialPageRoute(
              //             builder: (context) => const BaseLayout()));
              //   },
              // )

              child: MaterialButton(
                minWidth: double.infinity,
                height: 50,
                onPressed: () {
                  Navigator.push(
                      context,
                      MaterialPageRoute(
                          builder: (context) => const BaseLayout()));
                  Image.asset('Google__G__Logo.svg.png');
                },
                color: const Color.fromARGB(100, 22, 44, 33),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(30)),
                child: const Text(
                  "Google Sign In",
                  style: TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 16,
                    color: Color.fromARGB(225, 255, 255, 255),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 20),
            TextButton(
              //Login using OTP
              onPressed: () {
                Navigator.push(context,
                    MaterialPageRoute(builder: (context) => const Loginotp()));
              },
              child: const Text(
                'Login using OTP',
              ),
            ),
            const SizedBox(height: 30),
            TextButton(
              //forgot password screen
              onPressed: () {
                Navigator.push(
                    context,
                    MaterialPageRoute(
                        builder: (context) => const ForgotPassword()));
              },
              child: const Text(
                'Forgot Password?',
              ),
            ),
            const SizedBox(height: 20),
            Row(
              children: <Widget>[
                const Text('Does not have account?'),
                TextButton(
                  child: const Text(
                    'Register',
                    style: TextStyle(fontSize: 15),
                  ),
                  onPressed: () {
                    //signup screen
                    Navigator.push(
                        context,
                        MaterialPageRoute(
                            builder: (context) => const SignupPage()));
                  },
                )
              ],
              mainAxisAlignment: MainAxisAlignment.center,
            ),
          ],
        ));
  }
}
