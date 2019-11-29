#include <Python.h>

static PyObject *estou_a_ver(PyObject *self, PyObject *args) {
  printf("estou-a-ver\n");
  return Py_None;
}

static PyMethodDef methods[] = {
    {"estou_a_ver", estou_a_ver, METH_VARARGS, "Prints estou-a-ver"},
    {NULL, NULL, 0, NULL}};

static struct PyModuleDef module = {PyModuleDef_HEAD_INIT, "estouaver",
                                    "estou-a-ver C code extension module", -1,
                                    methods};

PyMODINIT_FUNC PyInit_estouaver(void) { return PyModule_Create(&module); }
