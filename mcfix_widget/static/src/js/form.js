odoo.define('mcfix_widget.relational_fields', function (require) {
    "use strict";
    var BasicModel = require('web.BasicModel');
    BasicModel.include({
        _getContext : function (element, options) {
            var res = this._super(element, options);
            var data = this._getEvalContext(element);
            if ('company_id' in data){
                if (data.company_id !== null){
                    res.mcfix_widget_company = data.company_id;
                }
            }
            return res;
        },
    });
});
