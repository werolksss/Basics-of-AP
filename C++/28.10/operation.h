#pragma once

struct IOperation {
    virtual double apply(double a, double b) = 0;
    virtual ~IOperation() = default;
};

using Create = IOperation* (*)(const char*);
using Destroy = void (*)(IOperation*);
