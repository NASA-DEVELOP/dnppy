from text_data_class import text_data
import os


class ioconfig(text_data):
    """
    An ioconfig object is an extension to the text_data_class
    it has the same methods of text_data_class, plus an add_param function
    and simplified save,load functions.

    It is used to generate "config" files, lists of important inputs to a set
    of complex functions. Allows you to save inputs and call them over and over
    again to avoid tedious input definitions, also facilitates good record keeping
    by keeping a hard file with a summary of all inputs alongside any outputs that
    might have been generated.

    be mindfull that "dict" and "list" type parameters will have each element assigned
    type "string"
    """

    # overrides
    def __init__(self, input_filepath = None):

        self.headers    = ["param_name".ljust(30), "param_type".ljust(18), "param_value"]
        self.row_data   = []        # standard text data object row_data formating
        self.conf_dict  = {}        # config dict of {param_name: param_value}

        if input_filepath and os.path.exists(input_filepath):
            self.load(input_filepath)
            
        return
    
    def __getitem__(self, index):
        return self.conf_dict[index]

    
    def add_param(self, param_names, param_values):
        """
        adds parameters to the ioconfig object
        
        param_name      A string, the name of the parameter
        param_value     may be any built-in datatype
        """

        # avoid indexing errors by handling list inputs differently
        if isinstance(param_names, list):
            for i,param in enumerate(param_names):
                entry = [param_names[i].ljust(30), str(type(param_values[i])).ljust(18), param_values[i]]
                self.row_data.append(entry)
        else:
            entry = [param_names.ljust(30), str(type(param_values)).ljust(18), param_values]
            self.row_data.append(entry)
            
        return


    def save(self, filepath):
        """ saves the contents of ioconfig object as text_data_object"""

        self.write_csv(filepath, delim = " ; ")
        return
        

    def load(self, filepath):
        """
        loads the contents of ioconfig object as a text data object

        interprets and formats each of the variables
        """

        self.read_csv(filepath, delim = " ; ")

        for i,row in enumerate(self.row_data):
            self.row_data[i][2] = self.interp(row[1], row[2])
            self.conf_dict[row[0].strip()] = row[2]

        print("imported config file '{0}'".format(filepath))
        print("keys                           : values")
        print("---------------------------------------")
        for key, value in self.conf_dict.iteritems():
            print("{0} : {1}".format(key.ljust(30),value))
        
        return

    def interp(self, in_type, in_value):
        """ wraps other interp functions into one """

        if "str" in in_type:
            return self.interp_str(in_value)

        elif "list" in in_type:
            return self.interp_list(in_value)

        elif "dict" in in_type:
            return self.interp_dict(in_value)
        
        elif "bool" in in_type:
            return self.interp_bool(in_value)

        elif "float" in in_type:
            return self.interp_float(in_value)

        elif "int" in in_type:
            return self.interp_int(in_value)
        
        elif "long" in in_type:
            return self.interp_long(in_value)

        elif "complex" in in_type:
            return self.interp_complex(in_value)

        elif "tuple" in in_type:
            return self.interp_tuple(in_value)

        else:
            raise TypeError("could not interpret input type '{0}'".format(in_type))
        
        
    def interp_str(self, in_str):
        return str(in_str)


    def interp_list(self, in_list):
        in_list = in_list.replace('[','').replace(']','').replace("'","")
        in_list = in_list.split(',')
        return in_list

    def interp_tuple(self, in_tuple):
        in_tuple = in_tuple.replace("(","").replace(")","").replace("'","").replace(" ","")
        return tuple(in_tuple.split(","))


    def interp_dict(self, in_dict):
        in_dict = in_dict.replace('{','').replace('}','').replace("'","")
        in_dict = in_dict.split(',')

        out_dict = {}
        
        for item in in_dict:
            item = item.split(":")
            out_dict[item[0]] = item[1]
            
        return out_dict


    def interp_bool(self, in_bool):
        return bool(in_bool)


    def interp_float(self, in_float):
        return float(in_float)


    def interp_int(self, in_int):
        return int(in_int)


    def interp_long(self, in_long):
        return long(in_long)


    def interp_complex(self, in_complex):
        return complex(in_complex.replace("(","").replace(")",""))
  


# testing area
if __name__ == "__main__":


    test_names = ["str",
                  "list",
                  "tuple",
                  "dict",
                  "bool",
                  "float",
                  "int",
                  "long",
                  "complex"]
    
    test_vals = ["test string",
                ["item 1","item 2", "item 3"],
                (1,2),
                {"one": 1, "two": 2},
                True,
                1.12345,
                1,
                1000000000000000000,
                1 + 1j]

    conf = ioconfig()
    conf.add_param(test_names, test_vals)
    conf.add_param("outfilepath","some filepath on my hard drive")
    conf.save("conf_test.txt")
    del conf
    
    conf = ioconfig("conf_test.txt")
    
