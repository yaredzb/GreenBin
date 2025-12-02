"""Table configurations and templates for GreenBin application."""

# --- Facilities View ---
FACILITIES_COLUMNS = [
    {"name": "id", "label": "Facility ID", "field": "id", "align": "left", "sortable": True},
    {"name": "loc", "label": "Location", "field": "loc", "align": "left"},
    {"name": "cap", "label": "Capacity", "field": "cap", "align": "center", "sortable": True},
    {"name": "eff", "label": "Efficiency", "field": "eff_val", "align": "left", "sortable": True}
]

FACILITIES_EFFICIENCY_SLOT = r'''
    <q-td :props="props">
        <div class="flex items-center gap-2">
            <q-linear-progress 
                :value="props.value / 100" 
                :color="props.value > 90 ? 'green' : props.value >= 70 ? 'orange' : 'red'"
                track-color="grey-3" 
                class="w-32" 
                size="8px"
                rounded
            />
            <span class="text-sm font-semibold">{{ props.value }}%</span>
        </div>
    </q-td>
'''

# --- Dashboard View ---
DASHBOARD_URGENT_COLUMNS = [
    {"name":"id","label":"Bin","field":"id"},
    {"name":"type","label":"Type","field":"waste_type"},
    {"name":"fill","label":"Fill %","field":"fill_level"},
    {"name":"status","label":"Status","field":"status"},
    {"name":"actions","label":"Actions","field":"actions"}
]

DASHBOARD_URGENT_ACTIONS_SLOT = r'''
    <q-td :props="props">
        <q-btn size="sm" color="red" label="Dispatch" @click="$parent.$emit('dispatch', props.row)" />
    </q-td>
'''

# --- History View ---
HISTORY_DISPATCH_COLUMNS = [
    {"name":"bin_id","label":"Bin ID","field":"bin_id", "align": "left"},
    {"name":"type","label":"Type","field":"type", "align": "left"},
    {"name":"dist","label":"Distance (km)","field":"distance", "align": "left"},
    {"name":"co2","label":"CO2 (kg)","field":"co2", "align": "left"},
    {"name":"time","label":"Time","field":"timestamp", "align": "left"},
]

HISTORY_UPDATE_COLUMNS = [
    {"name":"bin_id","label":"Bin ID","field":"bin_id", "align": "left"},
    {"name":"type","label":"Type","field":"type,", "align": "left"},
    {"name":"prev","label":"Prev Fill","field":"prev_fill", "align": "left"},
    {"name":"new","label":"New Fill","field":"new_fill", "align": "left"},
    {"name":"time","label":"Time","field":"timestamp", "align": "left"},
]

HISTORY_REQUEST_COLUMNS = [
    {"name":"bin_id","label":"Bin ID","field":"bin_id", "align": "left"},
    {"name":"type","label":"Type","field":"type", "align": "left"},
    {"name":"action","label":"Action","field":"action", "align": "left"},
    {"name":"time","label":"Time","field":"timestamp", "align": "left"},
]

# --- Requests View ---
REQUESTS_COLUMNS = [
    {"name": "bin_id", "label": "Bin ID", "field": "bin_id", "align": "left", "sortable": True},
    {"name": "time", "label": "Requested At", "field": "timestamp", "align": "left", "sortable": True},
    {"name": "status", "label": "Status", "field": "status", "align": "center"},
    {"name": "actions", "label": "Actions", "field": "actions", "align": "center"}
]

REQUESTS_STATUS_SLOT = r'''
    <q-td :props="props">
        <q-badge 
            :color="props.value === 'Pending' ? 'orange' : 
                    props.value === 'Processing' ? 'blue' : 
                    props.value === 'Completed' ? 'green' : 'grey'"
            :label="props.value"
            class="px-3 py-1"
        />
    </q-td>
'''

REQUESTS_ACTIONS_SLOT = r'''
    <q-td :props="props">
        <div class="flex gap-2 justify-center">
            <q-btn 
                size="sm" 
                flat
                dense
                icon="check_circle" 
                color="green"
                @click="$parent.$emit('approve', props.row)"
            >
                <q-tooltip>Approve request</q-tooltip>
            </q-btn>
            <q-btn 
                size="sm" 
                flat
                dense
                icon="cancel" 
                color="red"
                @click="$parent.$emit('reject', props.row)"
            >
                <q-tooltip>Reject request</q-tooltip>
            </q-btn>
        </div>
    </q-td>
'''

# --- Bins View ---
BINS_COLUMNS = [
    {"name": "id", "label": "Bin ID", "field": "id", "align": "left", "sortable": True},
    {"name": "type", "label": "Waste Type", "field": "waste_type", "align": "left", "sortable": True},
    {"name": "loc", "label": "Location", "field": "location", "align": "left"},
    {"name": "fill", "label": "Fill Level", "field": "fill_level", "align": "center", "sortable": True},
    {"name": "status", "label": "Status", "field": "status", "align": "center"},
    {"name": "actions", "label": "Actions", "field": "actions", "align": "center"}
]

BINS_FILL_SLOT = r'''
    <q-td :props="props">
        <div class="flex items-center justify-center gap-2">
            <q-linear-progress 
                :value="props.value / 100" 
                :color="props.value >= 80 ? 'red' : props.value >= 50 ? 'orange' : props.value >= 25 ? 'blue' : 'green'" 
                track-color="grey-3" 
                class="w-28" 
                size="8px"
                rounded
            />
            <span class="text-sm font-semibold">{{ props.value }}%</span>
        </div>
    </q-td>
'''

BINS_STATUS_SLOT = r'''
    <q-td :props="props">
        <q-badge 
            :color="props.value === 'Critical' ? 'red' : 
                   props.value === 'High' ? 'orange' : 
                   props.value === 'Medium' ? 'blue' : 
                   props.value === 'Low' ? 'green' : 'grey'"
            :label="props.value"
            class="px-3 py-1"
            style="min-width: 70px; display: inline-block; text-align: center;"
        />
    </q-td>
'''

BINS_ACTIONS_SLOT = r'''
    <q-td :props="props">
        <q-btn 
            size="sm" 
            label="Dispatch"
            color="primary"
            @click="$parent.$emit('dispatch', props.row)"
        />
    </q-td>
'''
