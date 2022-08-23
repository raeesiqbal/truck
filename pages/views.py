from multiprocessing import context
from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.views.generic import View
import datetime
from tablib import Dataset
from ortools.linear_solver import pywraplp
from django.template.loader import get_template
from xhtml2pdf import pisa

class HomeView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, "pages/home.html", context=context)


class FileView(View):
    def get(self, request, *args, **kwargs):
        context = {}
        return render(request, "pages/home.html", context=context)

    def post(self, request, *args, **kwargs):
        dataset = Dataset()
        new_resource = request.FILES["file"]
        if not new_resource.name.endswith("xlsx"):
            return render(
                request,
                "pages/home.html",
            )
        get_data = dataset.load(new_resource.read(), format="xlsx")
        raees = {}
        weights = []
        trucks = []
        bundle_numbers = []
        weights_nw = []
        for data in get_data:
            weights.append(data[2])
            trucks.append(data[0])
            bundle_numbers.append(data[1])
            weights_nw.append(data[3])
        raees['weights'] = weights
        raees['items'] = list(range(len(weights)))
        raees['bins'] = raees['items']
        if not request.POST["other_value"]:
            raees['bin_capacity'] = float(request.POST["bin_capacity"])
            print(float(request.POST["bin_capacity"]))
        else:
            print(float(request.POST["other_value"]))
            raees['bin_capacity'] = float(request.POST["other_value"])
        # Create the mip solver with the SCIP backend.
        solver = pywraplp.Solver.CreateSolver('SCIP')
        if not solver:
            return
        # Variables
        # x[i, j] = 1 if item i is packed in bin j.
        x = {}
        for i in raees['items']:
            for j in raees['bins']:
                x[(i, j)] = solver.IntVar(0, 1, 'x_%i_%i' % (i, j))
        # y[j] = 1 if bin j is used.
        y = {}
        for j in raees['bins']:
            y[j] = solver.IntVar(0, 1, 'y[%i]' % j)
        # Constraints
        # Each item must be in exactly one bin.
        for i in raees['items']:
            solver.Add(sum(x[i, j] for j in raees['bins']) == 1)
        # The amount packed in each bin cannot exceed its capacity.
        for j in raees['bins']:
            solver.Add(
                sum(x[(i, j)] * raees['weights'][i] for i in raees['items']) <= y[j] *
                raees['bin_capacity'])

        # Objective: minimize the number of bins used.
        solver.Minimize(solver.Sum([y[j] for j in raees['bins']]))
        status = solver.Solve()
        raees_dic = {}
        if status == pywraplp.Solver.OPTIMAL:
            num_bins = 0.
            for j in raees['bins']:
                if y[j].solution_value() == 1:
                    bin_items = []
                    bin_weight = 0
                    for i in raees['items']:
                        if x[i, j].solution_value() > 0:
                            bin_items.append(i)
                            bin_weight += raees['weights'][i]
                    if bin_weight > 0:
                        num_bins += 1
                        js = {}
                        print('Container number', j)
                        js["num"] = j
                        print('  Items packed:', bin_items)
                        js["items"] = bin_items
                        print('  Total weight:', bin_weight)
                        js["total"] = bin_weight
                        raees_dic[j]=js
                        print()
            for i in raees_dic:
                com_list = []
                for ii in raees_dic[i]["items"]:
                    com_dict = {}
                    get_truck = trucks[ii]
                    get_bundle = bundle_numbers[ii]
                    get_nw = weights_nw[ii]
                    get_gw = weights[ii]
                    com_dict["truck"] = get_truck
                    com_dict["bundle"] = get_bundle
                    com_dict["nw"] = get_nw
                    com_dict["gw"] = get_gw
                    com_list.append(com_dict)
                raees_dic[i]["data"] = com_list
            print(raees_dic)
        else:
            context = {
                "message":"The problem does not have an optimal solution."
            }
            print('The problem does not have an optimal solution.')
            return render(request, "home.html", context=context)
    
        template_path = "pages/page3.html"
        context = {
            "data":raees_dic
        }
        response = HttpResponse(content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="data.pdf"'
        template = get_template(template_path)
        html = template.render(context)

        # create a pdf
        pisa_status = pisa.CreatePDF(html, dest=response)
        # if error then show some funy view
        if pisa_status.err:
            return HttpResponse("We had some errors <pre>" + html + "</pre>")
        return response
        context ={
            "data":raees_dic
        }
        return render(request, "pages/page2.html", context=context)