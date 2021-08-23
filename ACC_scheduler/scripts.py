
for i in range(1,32):
    if i % 2 == 1:
        print('<div class="row bg-secondary text-white">')
    else:
        print('<div class="row">')
    print('<div class="col">0/'+str(i)+'</div>')
    print('<div class="col"><input class="form-check-input position-static" type="checkbox" name="survey-value" value="option'+str(i)+'-0" aria-label="..."></div>')
    print('<div class="col"><input class="form-check-input position-static" type="checkbox" name="survey-value" value="option' + str(
        i) + '-1" aria-label="..."></div>')
    print('<div class="col"><input class="form-check-input position-static" type="checkbox" name="survey-value" value="option' + str(
        i) + '-2" aria-label="..."></div>')
    print('<div class="col"><input class="form-check-input position-static" type="checkbox" name="survey-value" value="option' + str(
        i) + '-3" aria-label="..."></div>')
    print('<div class="col"><input class="form-check-input position-static" type="checkbox" name="survey-value" value="option' + str(
        i) + '-4" aria-label="..."></div>')
    print('<div class="col"><input class="form-check-input position-static" type="checkbox" name="survey-value" value="option' + str(
        i) + '-5" aria-label="..."></div>')
    print('</div>')