#include "operation.h"
#include <iostream>
#include <map>
#include <vector>
#include <string>
#include <sstream>
#include <cmath>
#include <dlfcn.h>
using namespace std;

struct Calculator {
    map<string, IOperation*> operations;

    double calculate(string name, double a, double b) {
        return operations.at(name)->apply(a, b);
    }
};

struct Module {
    void* handle;
    IOperation* operation;
    Destroy destroy;
};

int main(int argc, char** argv) {
    if (argc < 3 || argc % 2 == 0) {
        cerr << "Укажите пары: библиотека операция\n";
        return 1;
    }

    map<string, IOperation*> operations;
    vector<Module> modules;

    for (int i = 1; i < argc; i += 2) {
        void* handle = dlopen(argv[i], RTLD_NOW);
        if (!handle) {
            cerr << dlerror() << '\n';
            continue;
        }

        auto create = reinterpret_cast<Create>(dlsym(handle, "create"));
        auto destroy = reinterpret_cast<Destroy>(dlsym(handle, "destroy"));
        IOperation* operation = create && destroy ? create(argv[i + 1]) : nullptr;

        if (!operation) {
            cerr << "Не удалось загрузить " << argv[i + 1] << '\n';
            dlclose(handle);
            continue;
        }

        modules.push_back({handle, operation, destroy});
        operations[argv[i + 1]] = operation;
    }

    Calculator calculator{operations};
    string line, name;
    double a, b;
    cout << "Введите: операция a b. Выход: EXIT\n";

    while (getline(cin, line) && line != "EXIT") {
        istringstream input(line);
        string extra;

        if (!(input >> name >> a >> b) || (input >> extra) ||
            !operations.count(name)) {
            cout << "Неверная операция или числа\n";
            continue;
        }

        double result = calculator.calculate(name, a, b);
        if (isnan(result)) cout << "Операция не определена, проверьте делитель\n";
        else cout << result << '\n';
    }

    for (auto m : modules) {
        m.destroy(m.operation);
        dlclose(m.handle);
    }
}
