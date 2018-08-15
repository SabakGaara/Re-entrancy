import logging
import math
import six
from opcodes import *
from z3 import *
from z3.z3util import *
from vargenerator import *
from utils import *
import global_params

log = logging.getLogger(__name__)

# THIS IS TO DEFINE A SKELETON FOR ANALYSIS
# FOR NEW TYPE OF ANALYSIS: add necessary details to the skeleton functions

def set_cur_file(c_file):
    global cur_file
    cur_file = c_file

def init_analysis():
    analysis = {
        "gas": 0,
        "gas_mem": 0,
        "money_flow": [("Is", "Ia", "Iv")],  # (source, destination, amount)
        "reentrancy_bug":[],
        "money_concurrency_bug": [],
        "time_dependency_bug": {}
    }
    return analysis


# Money flow: (source, destination, amount)

def display_analysis(analysis):
    logging.debug("Money flow: " + str(analysis["money_flow"]))

# Check if this call has the Reentrancy bug
# Return true if it does, false otherwise
def check_reentrancy_bug(path_conditions_and_vars, stack, global_state,taint_stack):
    path_condition = path_conditions_and_vars["path_condition"]
    new_path_condition = []
    owner_path_condition = []
    amount_path_condition = []
    for expr in path_condition:
        if not is_expr(expr):
            continue
        list_vars = get_vars(expr)
        for var in list_vars:
            # check if a var is global
            if is_storage_var(var):
                pos = get_storage_position(var)
                if pos in global_state['Ia']:
                    new_path_condition.append(var == global_state['Ia'][pos])
    transfer_amount = stack[2]

    taint_recipient = taint_stack[1]
    taint_transfer_amount = taint_stack[2]
    target_recipient = ""
    target_transfer_amount= ""
    if taint_recipient == 1:
        target_recipient = "taint_target"
    if taint_transfer_amount == 1:
        target_transfer_amount = "taint transfer amount"

    if isSymbolic(transfer_amount) and is_storage_var(transfer_amount):
        pos = get_storage_position(transfer_amount)
        if pos in global_state['Ia']:
            new_path_condition.append(global_state['Ia'][pos] != 0)
    if global_params.DEBUG_MODE:
        log.info("=>>>>>> New PC: " + str(new_path_condition))

    solver = Solver()
    solver_owner = Solver()
    solver_amount = Solver()
    solver.set("timeout", global_params.TIMEOUT)
    solver.add(path_condition)
    solver.add(new_path_condition)
    solver_owner.set("timeout", global_params.TIMEOUT)
    solver_owner.add(path_condition)
    solver_owner.add(new_path_condition)
    solver_amount.set("timeout", global_params.TIMEOUT)
    solver_amount.add(path_condition)
    solver_amount.add(new_path_condition)
    # 2300 is the outgas used by transfer and send.
    # If outgas > 2300 when using call.gas.value then the contract will be considered to contain reentrancy bug
    solver.add(stack[0] > 2300)
    solver_amount.add(stack[0]>2300)
    solver_owner.add(stack[0]>2300)
    # transfer_amount > deposit_amount => reentrancy
    # solver.add(stack[2] > BitVec('Iv', 256))
    # if it is not feasible to re-execute the call, its not a bug
    ret_val = not (solver.check() == unsat)
    #log.info("Reentrancy_bug? " + str(ret_val))
    if ret_val:
        ms_condition = ""
        for condition in path_condition:
            if (str(condition).find('Is) ==') >= 0) or (str(condition).find("== Extract(159, 0, Is)") >= 0):
                ms_condition = str(condition)
                break
        if ms_condition != "":
            ms_owner = ms_condition.find("Ia_store")
            if ms_owner >= 0:
                ms_owner_key = ms_condition.split('-')
                try:
                    ms_owner_num = int(ms_owner_key[1])
                except:
                    ms_owner_num = ms_owner_key[1]
                if ms_owner_num in global_params.PATH_CONDITION:
                    if global_params.PATH_CONDITION[ms_owner_num] == 0:
                        log.info("Onlyowner not worked")
                        if taint_recipient:
                            log.info("taint_target")
                    # else:
                    #     log.info("Onlyowner worked")
                else:
                    global_params.PATH_CONDITION[ms_owner_num] = 1
<<<<<<< HEAD
                    if taint_recipient:
                        log.info("taint_target if onlyower not worked")
            # else:
            #     log.info("It does not matter with syExec")
            elif target_recipient:
                log.info(target_recipient)
                if taint_transfer_amount:
                    log.info(target_transfer_amount)
            if not taint_recipient:
                result = []
                for single in stack:
                    res = str(single).find("Ia_store")
                    if res >= 0:
                        res1 = str(single).split('-')
                        result.append(res1[1])
                if len(result) != 0:
                    for var_address in result:
                        try:
                            var_address = int(var_address)
                        except:
                            var_address = var_address
                        if var_address in global_params.VAR_STATE_GLOBAL:
                            if global_params.VAR_STATE_GLOBAL[var_address] == 2:
                                # log.info("taint_happen in:")
                                # log.info(global_state["Ia"][var_address])
                                if var_address in global_params.SSTORE_STACK:
                                    # log.info("recipent success")
                                    for condition in global_params.SSTORE_STACK[var_address]:
                                        #   log.info("recipient success")
                                        owner_path_condition.append(condition)
                                        solver_owner.add(condition)
                                    result = not (solver_owner.check == unsat)
                                    if result:
                                        log.info("taint_happen in:")
                                        log.info(global_state["Ia"][var_address])
                                        log.info("path_condition is satisfied")
                            # if var_address in global_params.PATH_CONDITION:
                            #     if global_params.PATH_CONDITION[var_address] == 2:
                            #         log.info("Taint target onlyowner, no bug")
                            #     elif global_params.PATH_CONDITION[var_address] == 1:
                            #         log.info("Taint target have not onlyowner,taint bug")
=======
            else:
                log.info("It does not matter with syExec")
        if target_recipient:
            log.info(target_recipient)
        if taint_transfer_amount:
            log.info(target_transfer_amount)
        result = []
        for single in stack:
            res = str(single).find("Ia_store")
            if res >= 0:
                res1 = str(single).split('-')
                result.append(res1[1])
        if len(result) != 0:
            for var_address in result:
                try:
                    var_address = int(var_address)
                except:
                    var_address = var_address
                if var_address in global_params.VAR_STATE_GLOBAL:
                    if global_params.VAR_STATE_GLOBAL[var_address] == 2:
                        log.info("taint_happen in:")
                        log.info(global_state["Ia"][var_address])
                        if var_address in global_params.SSTORE_STACK:
                           # log.info("recipent success")
                           for condition in global_params.SSTORE_STACK[var_address]:
                               #   log.info("recipient success")
                               owner_path_condition.append(condition)
                               solver_owner.add(condition)
                           result = not (solver_owner.check == unsat)
                           if result:
                               log.info("path_condition is satisfied")
                        if var_address in global_params.PATH_CONDITION:
                            if global_params.PATH_CONDITION[var_address] == 2:
                                log.info("Taint target onlyowner, no bug")
                            elif global_params.PATH_CONDITION[var_address] == 1:
                                log.info("Taint target have not onlyowner,taint bug")
>>>>>>> b80472f1d93640c7dd986157e3e81ec17e5a341c

                        else:
                            # log.info(var_address)
                            global_params.VAR_STATE_GLOBAL[var_address] = 1

                            # log.info(global_params.VAR_STATE_GLOBAL[int(var_address)])
                            log.info("wait")
                            if not (var_address in global_params.SSTORE_STACK):
                                global_params.SSTORE_STACK[var_address] = []
                            global_params.SSTORE_STACK[var_address].append(path_conditions_and_vars["path_condition"])
                    # log.info(path_conditions_and_vars["path_condition"])
                    #  if not (var_address in global_params.PATH_CONDITION):
                    #      global_params.PATH_CONDITION[var_address] = 3

        else:
            log.info("it does not matter")
    return ret_val

def calculate_gas(opcode, stack, mem, global_state, analysis, solver):
    gas_increment = get_ins_cost(opcode) # base cost
    gas_memory = analysis["gas_mem"]
    # In some opcodes, gas cost is not only depend on opcode itself but also current state of evm
    # For symbolic variables, we only add base cost part for simplicity
    if opcode in ("LOG0", "LOG1", "LOG2", "LOG3", "LOG4") and len(stack) > 1:
        if isReal(stack[1]):
            gas_increment += GCOST["Glogdata"] * stack[1]
    elif opcode == "EXP" and len(stack) > 1:
        if isReal(stack[1]) and stack[1] > 0:
            gas_increment += GCOST["Gexpbyte"] * (1 + math.floor(math.log(stack[1], 256)))
    elif opcode == "EXTCODECOPY" and len(stack) > 2:
        if isReal(stack[2]):
            gas_increment += GCOST["Gcopy"] * math.ceil(stack[2] / 32)
    elif opcode in ("CALLDATACOPY", "CODECOPY") and len(stack) > 3:
        if isReal(stack[3]):
            gas_increment += GCOST["Gcopy"] * math.ceil(stack[3] / 32)
    elif opcode == "SSTORE" and len(stack) > 1:
        if isReal(stack[1]):
            try:
                try:
                    storage_value = global_state["Ia"][int(stack[0])]
                except:
                    storage_value = global_state["Ia"][str(stack[0])]
                # when we change storage value from zero to non-zero
                if storage_value == 0 and stack[1] != 0:
                    gas_increment += GCOST["Gsset"]
                else:
                    gas_increment += GCOST["Gsreset"]
            except: # when storage address at considered key is empty
                if stack[1] != 0:
                    gas_increment += GCOST["Gsset"]
                elif stack[1] == 0:
                    gas_increment += GCOST["Gsreset"]
        else:
            try:
                try:
                    storage_value = global_state["Ia"][int(stack[0])]
                except:
                    storage_value = global_state["Ia"][str(stack[0])]
                solver.push()
                solver.add(Not( And(storage_value == 0, stack[1] != 0) ))
                if solver.check() == unsat:
                    gas_increment += GCOST["Gsset"]
                else:
                    gas_increment += GCOST["Gsreset"]
                solver.pop()
            except Exception as e:
                if str(e) == "canceled":
                    solver.pop()
                solver.push()
                solver.add(Not( stack[1] != 0 ))
                if solver.check() == unsat:
                    gas_increment += GCOST["Gsset"]
                else:
                    gas_increment += GCOST["Gsreset"]
                solver.pop()
    elif opcode == "SUICIDE" and len(stack) > 1:
        if isReal(stack[1]):
            address = stack[1] % 2**160
            if address not in global_state:
                gas_increment += GCOST["Gnewaccount"]
        else:
            address = str(stack[1])
            if address not in global_state:
                gas_increment += GCOST["Gnewaccount"]
    elif opcode in ("CALL", "CALLCODE", "DELEGATECALL") and len(stack) > 2:
        # Not fully correct yet
        gas_increment += GCOST["Gcall"]
        if isReal(stack[2]):
            if stack[2] != 0:
                gas_increment += GCOST["Gcallvalue"]
        else:
            solver.push()
            solver.add(Not (stack[2] != 0))
            if check_sat(solver) == unsat:
                gas_increment += GCOST["Gcallvalue"]
            solver.pop()
    elif opcode == "SHA3" and isReal(stack[1]):
        pass # Not handle


    #Calculate gas memory, add it to total gas used
    length = len(mem.keys()) # number of memory words
    new_gas_memory = GCOST["Gmemory"] * length + (length ** 2) // 512
    gas_increment += new_gas_memory - gas_memory

    return (gas_increment, new_gas_memory)

def update_analysis(analysis, opcode, stack, mem, global_state, path_conditions_and_vars, solver,taint_stack):
    gas_increment, gas_memory = calculate_gas(opcode, stack, mem, global_state, analysis, solver)
    analysis["gas"] += gas_increment
    analysis["gas_mem"] = gas_memory

    if opcode == "CALL":
        # log.info(stack)
        # # log.info(taint_stack)
        # if int(0) in global_params.VAR_STATE_GLOBAL:
        #     log.info("it worked")
        #     log.info(global_params.VAR_STATE_GLOBAL[0])
        recipient = stack[1]
        transfer_amount = stack[2]
        # log.info("update")
        # log.info(recipient)
        #  log.info("i am in")
        #if isReal(transfer_amount) and transfer_amount == 0:
         #   return
        if isSymbolic(recipient):
            recipient = simplify(recipient)

        reentrancy_result = check_reentrancy_bug(path_conditions_and_vars, stack, global_state, taint_stack)
        analysis["reentrancy_bug"].append(reentrancy_result)

        analysis["money_concurrency_bug"].append(global_state["pc"])
        analysis["money_flow"].append( ("Ia", str(recipient), str(transfer_amount)))
    elif opcode == "SUICIDE":
        recipient = stack[0]
        if isSymbolic(recipient):
            recipient = simplify(recipient)
        analysis['money_concurrency_bug'].append(global_state['pc'])
        analysis["money_flow"].append(("Ia", str(recipient), "all_remaining"))

# Check if it is possible to execute a path after a previous path
# Previous path has prev_pc (previous path condition) and set global state variables as in gstate (only storage values)
# Current path has curr_pc
def is_feasible(prev_pc, gstate, curr_pc):
    curr_pc = list(curr_pc)
    new_pc = []
    for var in get_all_vars(curr_pc):
        if is_storage_var(var):
            pos = get_storage_position(var)
            if pos in gstate:
                new_pc.append(var == gstate[pos])
    curr_pc += new_pc
    curr_pc += prev_pc
    solver = Solver()
    solver.set("timeout", global_params.TIMEOUT)
    solver.add(curr_pc)
    if solver.check() == unsat:
        return False
    else:
        return True


# detect if two flows are not really having race condition, i.e. check if executing path j
# after path i is possible.
# 1. We first start with a simple check to see if a path edit some storage variable
# which makes the other path infeasible
# 2. We then check if two paths cannot be executed next to each other, for example they
# are two paths yielded from this branch condition ``if (locked)"
# 3. More checks are to come
def is_false_positive(i, j, all_gs, path_conditions):
    pathi = path_conditions[i]
    pathj = path_conditions[j]
    statei = all_gs[i]

    # rename global variables in path i
    set_of_pcs, statei = rename_vars(pathi, statei)
    log.debug("Set of PCs after renaming global vars" + str(set_of_pcs))
    log.debug("Global state values in path " + str(i) + " after renaming: " + str(statei))
    if is_feasible(set_of_pcs, statei, pathj):
        return False
    else:
        return True


# Simple check if two flows of money are different
def is_diff(flow1, flow2):
    if len(flow1) != len(flow2):
        return 1
    n = len(flow1)
    for i in range(n):
        if flow1[i] == flow2[i]:
            continue
        try:
            tx_cd = Or(Not(flow1[i][0] == flow2[i][0]),
                       Not(flow1[i][1] == flow2[i][1]),
                       Not(flow1[i][2] == flow2[i][2]))
            solver = Solver()
            solver.set("timeout", global_params.TIMEOUT)
            solver.add(tx_cd)

            if solver.check() == sat:
                return 1
        except Exception as e:
            return 1
    return 0
