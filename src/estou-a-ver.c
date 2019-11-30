#include <Python.h>

// Creating a C function that extends python:
// static PyObject *function_name(PyObject *self, PyObject *args)

static PyObject *estou_a_ver() {
  printf("estou-a-ver\n");
  return Py_None;
}

// Adding the C function to the method list:
// {"function_name", function_name, METH_VARARGS, "Function docstring"},

static PyMethodDef methods[] = {
    {"estou_a_ver", estou_a_ver, METH_VARARGS, "Prints estou-a-ver"},
    {NULL, NULL, 0, NULL}};

// Creating the C extension module

static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "estouaver",
                                    "estou-a-ver C code extension module", -1,
                                    methods};

PyMODINIT_FUNC PyInit_estouaver(void) { return PyModule_Create(&module); }
