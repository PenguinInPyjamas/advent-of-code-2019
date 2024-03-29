from collections import defaultdict


def run_intcode(program_ints, input_iterator, debug=False):
    tape = defaultdict(lambda: 0)
    for i, v in enumerate(program_ints):
        tape[i] = v
    head = 0
    relative_base = 0
    while head < len(tape):
        if debug:
            debug_print_tape(tape, head)
        intcode = tape[head]
        opcode = intcode % 100
        if opcode == 1:
            # Add
            lhs, rhs, out = calculate_args(intcode, tape, head, 3)
            if debug:
                print(f"01 add {arg_to_string(tape, lhs)}, {arg_to_string(tape, rhs)}, {arg_to_string(tape, out)}")
            write_at_parameter(tape, out, read_at_parameter(tape, lhs, relative_base) + read_at_parameter(tape, rhs, relative_base), relative_base)
            head += 4
        elif opcode == 2:
            # Multiply
            lhs, rhs, out = calculate_args(intcode, tape, head, 3)
            if debug:
                print(f"02 multiply {arg_to_string(tape, lhs)}, {arg_to_string(tape, rhs)}, {arg_to_string(tape, out)}")
            write_at_parameter(tape, out, read_at_parameter(tape, lhs, relative_base) * read_at_parameter(tape, rhs, relative_base), relative_base)
            head += 4
        elif opcode == 3:
            # Input
            arg, = calculate_args(intcode, tape, head, 1)
            try:
                next_input = next(input_iterator)
            except StopIteration:
                if debug:
                    print(f"03 input (NO INPUT LEFT!)")
                break
            if debug:
                print(f"03 input {arg_to_string(tape, arg)}, {next_input}")
            write_at_parameter(tape, arg, next_input, relative_base)
            head += 2
        elif opcode == 4:
            # Output
            arg, = calculate_args(intcode, tape, head, 1)
            if debug:
                print(f"04 output {arg_to_string(tape, arg)}")
            output = read_at_parameter(tape, arg, relative_base)
            head += 2
            yield output
        elif opcode == 5:
            # Jump if true
            cond, new_head = calculate_args(intcode, tape, head, 2)
            if debug:
                print(f"05 jump-if-true {arg_to_string(tape, cond)}, {arg_to_string(tape, new_head)}")
            if read_at_parameter(tape, cond, relative_base) != 0:
                head = read_at_parameter(tape, new_head, relative_base)
            else:
                head += 3
        elif opcode == 6:
            # Jump if false
            cond, new_head = calculate_args(intcode, tape, head, 2)
            if debug:
                print(f"06 jump-if-false {arg_to_string(tape, cond)}, {arg_to_string(tape, new_head)}")
            if read_at_parameter(tape, cond, relative_base) == 0:
                head = read_at_parameter(tape, new_head, relative_base)
            else:
                head += 3
        elif opcode == 7:
            # Less than
            lhs, rhs, out = calculate_args(intcode, tape, head, 3)
            if debug:
                print(f"07 less-than {arg_to_string(tape, lhs)}, {arg_to_string(tape, rhs)}, {arg_to_string(tape, out)}")
            result = 1 if read_at_parameter(tape, lhs, relative_base) < read_at_parameter(tape, rhs, relative_base) else 0
            write_at_parameter(tape, out, result, relative_base)
            head += 4
        elif opcode == 8:
            # Equals
            lhs, rhs, out = calculate_args(intcode, tape, head, 3)
            if debug:
                print(f"08 equals {arg_to_string(tape, lhs)}, {arg_to_string(tape, rhs)}, {arg_to_string(tape, out)}")
            result = 1 if read_at_parameter(tape, lhs, relative_base) == read_at_parameter(tape, rhs, relative_base) else 0
            write_at_parameter(tape, out, result, relative_base)
            head += 4
        elif opcode == 9:
            # Set relative base
            (arg,) = calculate_args(intcode, tape, head, 1)
            relative_base += read_at_parameter(tape, arg, relative_base)
            head += 2
        elif opcode == 99:
            if debug:
                print(f"99 STOP")
            break
        else:
            raise Exception(f"Unknown opcode '{opcode}'")
    return tape


def calculate_args(intcode, tape, head, num_args):
    return [((intcode // (10 ** (arg_num + 2))) % 10, tape[head + arg_num + 1]) for arg_num in range(num_args)]


def read_at_parameter(tape, param, relative_base):
    mode, value = param
    if mode == 0:
        # Position
        return tape[value]
    elif mode == 1:
        # Immediate
        return value
    elif mode == 2:
        # Relative
        return tape[value + relative_base]
    else:
        raise Exception(f"Invalid parameter mode '{mode}'")


def write_at_parameter(tape, param, new_value, relative_base):
    mode, value = param
    if mode == 0:
        # Position
        tape[value] = new_value
    elif mode == 1:
        # Immediate
        raise Exception(f"Can't write to immediate parameter '{mode}'")
    elif mode == 2:
        # Relative
        tape[value + relative_base] = new_value
    else:
        raise Exception(f"Invalid parameter mode '{mode}'")


def debug_print_tape(tape, head):
    print(", ".join(
        [(f"___{i}:{str(tape[i])}___" if i == head else f"{i}:{str(tape[i])}")
         for i in range(len(tape))]
    ) + "\n")


def arg_to_string(tape, arg):
    mode, value = arg
    if mode == 0:
        return f"pos:{value}({tape[value]})"
    elif mode == 1:
        return f"imm:{value}"
    else:
        return f"invalid({mode}){value}"


def lambda_to_generator(func):
    while True:
        yield func()
