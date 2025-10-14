# main.py
from model.data_model import DataModel
from view.main_window import MainWindow
from controller.app_controller import AppController

if __name__ == "__main__":
    # 1. Initialize the Model
    model = DataModel()

    # 2. Initialize the Controller and link it to the Model
    controller = AppController(model)

    # 3. Initialize the View and link it to the Controller
    view = MainWindow(controller)
    
    # 4. Link the View back to the Controller
    controller.set_view(view)

    # 5. Start the application's main loop
    view.mainloop()