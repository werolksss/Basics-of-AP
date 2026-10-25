#include "operation.h"
#include <string>
#include <limits>
using namespace std;

struct Add : IOperation {
    double apply(double a, double b) override { return a + b; }
};
struct Sub : IOperation {
    double apply(double a, double b) override { return a - b; }
};
struct Mul : IOperation {
    double apply(double a, double b) override { return a * b; }
};
struct Div : IOperation {
    double apply(double a, double b) override {
        return b == 0 ? numeric_limits<double>::quiet_NaN() : a / b;
    }
};

extern "C" IOperation* create(const char* name) {
    string n = name;
    if (n == "Add") return new Add;
    if (n == "Sub") return new Sub;
    if (n == "Mul") return new Mul;
    if (n == "Div") return new Div;
    return nullptr;
}

extern "C" void destroy(IOperation* operation) {
    delete operation;
}
