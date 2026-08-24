import 'package:customertracker/register_details.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class SignupPage extends StatelessWidget {
  const SignupPage({super.key});

  @override
  Widget build(BuildContext context) => Scaffold(
        resizeToAvoidBottomInset: false,
        backgroundColor: const Color.fromARGB(255, 253, 253, 253),
        appBar: AppBar(
          title: const Text(
            'Euphoria Infotech (I) Pvt Ltd',
            style: TextStyle(fontSize: 17),
          ),
          elevation: 0,
          backgroundColor: const Color.fromARGB(255, 91, 92, 92),
          leading: IconButton(
              onPressed: () {
                Navigator.pop(context);
              },
              icon: const Icon(
                Icons.arrow_back_ios,
                size: 20,
                color: Color.fromARGB(255, 232, 232, 233),
              )),
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
            child: SingleChildScrollView(
              child: SizedBox(
                height: MediaQuery.of(context).size.height,
                width: double.infinity,
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      children: [
                        const Column(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            Text(
                              "Register",
                              style: TextStyle(
                                fontSize: 30,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            SizedBox(
                              height: 20,
                            ),
                            Text(
                              "Create an Account",
                              style: TextStyle(
                                fontSize: 15,
                                color: Color.fromARGB(255, 65, 64, 64),
                              ),
                            ),
                            SizedBox(
                              height: 20,
                            )
                          ],
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 30),
                          child: Column(
                            children: [
                              makeInput(label: "Email"),
                              makeInput(label: "Password", obsureText: true),
                              makeInput(
                                  label: "Confirm Pasword", obsureText: true)
                            ],
                          ),
                        ),
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 40),
                          child: Container(
                            padding: const EdgeInsets.only(top: 4, left: 4),
                            child: MaterialButton(
                              minWidth: double.infinity,
                              height: 60,
                              onPressed: () {
                                Navigator.push(
                                    context,
                                    MaterialPageRoute(
                                        builder: (context) =>
                                            const Register()));
                              },
                              color: const Color.fromARGB(100, 22, 44, 33),
                              shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(40)),
                              child: const Text(
                                "Register",
                                style: TextStyle(
                                  fontWeight: FontWeight.w600,
                                  fontSize: 16,
                                  color: Color.fromARGB(204, 255, 255, 255),
                                ),
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(
                          height: 20,
                        ),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: <Widget>[
                            const Text("Already have an account?"),
                            TextButton(
                              child: const Text(
                                'Login',
                                style: TextStyle(
                                    color: Color.fromARGB(255, 65, 64, 64),
                                    fontSize: 20),
                              ),
                              onPressed: () {
                                Navigator.pop(context);
                              },
                            ),
                          ],
                        )
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );
}

Widget makeInput({label, obsureText = false}) {
  return Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(
        label,
        style: const TextStyle(
            fontSize: 15,
            fontWeight: FontWeight.w400,
            color: Color.fromARGB(255, 7, 7, 7)),
      ),
      const SizedBox(
        height: 5,
      ),
      TextField(
        obscureText: obsureText,
        decoration: const InputDecoration(
          contentPadding: EdgeInsets.symmetric(vertical: 0, horizontal: 10),
          enabledBorder: OutlineInputBorder(
            borderSide: BorderSide(
              color: Color.fromARGB(255, 3, 3, 3),
            ),
          ),
          border: OutlineInputBorder(
              borderSide: BorderSide(color: Color.fromARGB(255, 8, 8, 8))),
        ),
      ),
      const SizedBox(
        height: 30,
      )
    ],
  );
}
