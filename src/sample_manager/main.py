from sample_manager.app.controller import ApplicationController


def main():

    app = ApplicationController()

    print("Sample Manager CLI")
    print("Type 'exit' to quit")

    while True:

        user_input = input("> ")

        if user_input in ("exit", "quit"):
            break

        result = app.handle_input(user_input)

        if result:
            print(result)


if __name__ == "__main__":
    main()
