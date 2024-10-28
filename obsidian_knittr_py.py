from modules.DynamicArguments import OT


# Example usage
def main():
    try:
        config_file = "DynamicArguments.ini"
        ot = OT(config_file=config_file, format="quarto::pdf")
        bAutoSubmitOTGUI = False
        x = 600
        y = 800
        if bAutoSubmitOTGUI:
            ot.SkipGUI = bAutoSubmitOTGUI
        ot.generate_gui(x, y, True, "ParamsGUI:", 1, 1, 674, 1)

        print("Loaded arguments:", ot.arguments)
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
