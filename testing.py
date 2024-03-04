import PySimpleGUI as sg
import datetime as dt
import DBCon  # Database connectivity
import ExamControlFunctions as FN  # Defined functions library

# Global Variables
weekdays = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
slots = ['Morning', 'Afternoon']

# Database connection object
DB = DBCon.DB

# List of all departments in college
programmes = [i[0] for i in FN.get_all_data('SHOW TABLES FROM students;')]

# Layout for the GUI
layout = [
    [sg.Text('Enter the name of the exam:'), sg.InputText(key='-EXAM_NAME-')],
    [sg.Text('Enter the date of the exam (DD-MM-YYYY):'), sg.InputText(key='-EXAM_DATE-')],
    [sg.Text('Enter the slot of the exam (Morning/Afternoon):'), sg.Combo(slots, key='-EXAM_SLOT-')],
    [sg.Text('Enter the course code of the paper (Press OK when done):')],
    [sg.InputText(key='-PAPER_INPUT-'), sg.Button('OK')],
    [sg.Text(size=(60, 1), key='-OUTPUT-')],
    [sg.Button('Submit'), sg.Button('Exit')]
]

# Create the GUI window
window = sg.Window('Exam Schedule').Layout(layout)

# Function to handle button click event
def on_button_click():
    exam_name = values['-EXAM_NAME-']
    exam_date_str = values['-EXAM_DATE-']
    exam_slot = values['-EXAM_SLOT-']

    try:
        exam_date = dt.datetime.strptime(exam_date_str, '%d-%m-%Y')
        exam_day = weekdays[exam_date.weekday()]
        exam_slot_index = 1 if exam_slot == 'Afternoon' else 0

        # Logic to fetch papers and related information
        papers = []
        paper_programme = {}
        paper_students = {}
        paper_students_count = {}

        # Extracting paper inputs
        paper_input = values['-PAPER_INPUT-'].strip()
        while paper_input:
            papers.append(paper_input)
            paper_input = sg.popup_get_text('Enter the course code of the paper (Press Cancel when done):')

        # Adding different programmes for each paper
        for i in papers:
            paper_programme[i] = []
            paper_students[i] = []
            temp = programmes.copy()
            while True:
                programme_index = sg.popup_get_index(f"Select programme for {i}", f"Programmes List: {temp}", modal=True)
                if programme_index == None:
                    break
                loop_temp = temp.pop(programme_index)
                paper_programme[i].append(loop_temp)
                paper_students[i] += ([k[0] for k in FN.get_all_data(f'SELECT prn FROM students.{loop_temp}')])

                if sg.popup_yes_no(f"Add students from another programme to {i}?") != 'Yes':
                    break

                while True:
                    decision = sg.popup_yes_no_cancel(f"Do you want to manually add or remove the students from the list for {i}?")
                    if decision == 'Yes':
                        prn = sg.popup_get_text('Enter the PRN of the student to add to the list:', modal=True)
                        if prn and prn not in paper_students[i]:
                            paper_students[i].append(prn)
                        else:
                            sg.popup_error('PRN already exists in the list.')
                    elif decision == 'No':
                        prn = sg.popup_get_text('Enter the PRN of the student to remove from the list:', modal=True)
                        if prn and prn in paper_students[i]:
                            paper_students[i].remove(prn)
                        else:
                            sg.popup_error('PRN does not exist in the list.')
                    else:
                        break

            paper_students_count[i] = len(paper_students[i])

        # Displaying output
        output_text = f"{exam_name}\n{exam_date_str}\n{exam_day}\n{exam_slot}\n"
        output_text += f"{paper_programme}\n{paper_students}\n{paper_students_count}"
        window['-OUTPUT-'].update(output_text)

    except ValueError:
        sg.popup_error("Invalid Date Format. Please enter date in DD-MM-YYYY format.")

# Event loop
while True:
    event, values = window.Read()
    if event is None or event == 'Exit':
        break
    elif event == 'OK':
        paper_input = values['-PAPER_INPUT-'].strip()
        if paper_input:
            window['-PAPER_INPUT-'].update('')
            window['-PAPER_INPUT-'].Update(value=f'{paper_input}\n')
        else:
            sg.popup_error("Please enter a valid course code.")
    elif event == 'Submit':
        on_button_click()

window.Close()
