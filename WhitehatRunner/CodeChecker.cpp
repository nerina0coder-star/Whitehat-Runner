#include <algorithm>
#include <vector>
#include <string>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/eval.h>
#include <exception>

namespace py = pybind11;

#include <cctype>

bool codecheck(std::string code) {
    std::vector<int> uscores;

    int count = std::count(code.begin(), code.end(), ',');
    bool out = true;


    if (count != 0) {
        try {
            for (int i = 0; i < count;i++) {
                 out = codecheck(code.substr(0, code.find(','))) && out;
                 code = code.substr(code.find(',') + 1, code.length());
            }
        } catch (std::exception _) {
            py::print(_.what());
        }
        out = codecheck(code) && out;
        return out;
    }
    std::string target = "__";
    auto found = std::search(code.begin(), code.end(), target.begin(), target.end());

    if (code.end() == found) {
        out = true;
    }
    else {
        while (true) {
            auto found = std::search(code.begin(), code.end(), target.begin(), target.end());
            if (code.end() == found) { break; }
            int index = code.find(target);
            int secondi = code.find(target, index + 1);
            if (secondi == -1) { break; }
            if (index == secondi) { break; }
            std::string searching = code.substr(index, code.find(target, index + 1));
            bool is_identifier = py::str(searching).attr("isidentifier")().cast<bool>();
            if (is_identifier) { out = false; break; }
            code = code.substr(secondi + 2);
        }
    }

    // TODO

    
    return out;
}

PYBIND11_MODULE(CodeCheck, m) {
    m.def("check", &codecheck, "Checks if the given code is calling anything that starts with __ and is an identifier.");
}
